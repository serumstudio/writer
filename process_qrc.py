# -*- coding: utf-8 -*-
"""Script to process QRC files (convert .qrc to _rc.py and .rcc).

The script will attempt to compile the qrc file using the following tools:

    - pyrcc4 for PyQt4 and PyQtGraph (Python)
    - pyrcc5 for PyQt5 and QtPy (Python)
    - pyside-rcc for PySide (Python)
    - pyside2-rcc for PySide2 (Python)
    - rcc for Qt4 and Qt5 (C++)

Delete the compiled files that you don't want to use manually after
running this script.

Links to understand those tools:

    - pyrcc4: http://pyqt.sourceforge.net/Docs/PyQt4/resources.html#pyrcc4
    - pyrcc5: http://pyqt.sourceforge.net/Docs/PyQt5/resources.html#pyrcc5
    - pyside-rcc: https://www.mankier.com/1/pyside-rcc
    - pyside2-rcc: https://doc.qt.io/qtforpython/overviews/resources.html (Documentation Incomplete)
    - rcc on Qt4: http://doc.qt.io/archives/qt-4.8/rcc.html
    - rcc on Qt5: http://doc.qt.io/qt-5/rcc.html

"""

# Standard library imports

import os
import shutil
import sys
import glob
from loguru import logger
import argparse
from subprocess import call


# Local imports
import SerumWriter.Lib.Modern as Modern
from SerumWriter.Lib.Modern import RESOURCE_PATH, STYLES_PATH, QRC_FILE, QSS_FILE
from SerumWriter.Lib.Modern.Utils.images import  (
    create_images, 
    create_palette_image, 
    generate_qrc_file, 
    create_titlebar_images,
    fonts
)
from SerumWriter.Lib.Modern.Utils.scss import create_qss

def run_process(args):
    """Process qrc files."""

    import inspect
    import SerumWriter.Lib.Modern.Palette as source

    palettes = []
    for name, obj in inspect.getmembers(source):
        if inspect.isclass(obj) and issubclass(obj, source.BasePalette) and obj is not source.BasePalette:
            palettes.append(obj)

    logger.debug("Found palettes: " + str(palettes))

    for palette in palettes:
        palette_name = str(palette.__name__)
        logger.debug("Generating files for: " + palette_name)

        # create directory for every style in palette.py
        os.chdir(STYLES_PATH)
        os.makedirs(palette_name, exist_ok=True)
        os.chdir(os.path.join(STYLES_PATH, palette_name))
        open("__init__.py", "w+").close()

        output_dir = os.path.join(STYLES_PATH, palette_name)

        font_path = os.path.join(output_dir, 'fonts')
        logger.info('Copying fonts: %s' % (font_path))
        if os.path.exists(font_path):
            #: Re write
            shutil.rmtree(font_path)

        shutil.copytree(fonts.absolute(), font_path)

        # get paths to output directories for this palette
        images_dir = os.path.join(output_dir, 'images')
        rc_dir = os.path.join(output_dir, 'rc')
        # qss_dir = os.path.join(output_dir, 'qss')

        # create directories
        os.makedirs(images_dir, exist_ok=True)
        os.makedirs(rc_dir, exist_ok=True)
        # os.makedirs(qss_dir, exist_ok=True)

        qrc_filepath = os.path.join(output_dir, QRC_FILE)
        qss_filepath = os.path.join(output_dir, QSS_FILE)
        # variables_scss_filepath = os.path.join(qss_dir, VARIABLES_SCSS_FILE)

        # Create palette and resources png images
        logger.debug('Generating palette image ...')
        create_palette_image(palette=palette, path=images_dir)

        logger.debug('Generating images ...')
        create_images(palette=palette, rc_path=rc_dir)

        logger.debug("Generating images for titlebar buttons")
        create_titlebar_images(rc_path=rc_dir, palette=palette)

        logger.debug('Generating qrc ...')
        generate_qrc_file(rc_path=rc_dir, qrc_path=qrc_filepath)

        logger.debug('Converting .qrc to _rc.py and/or .rcc ...')

        for qrc_file in glob.glob('*.qrc'):
            # get name without extension
            filename = os.path.splitext(qrc_file)[0]

            logger.debug(filename + '...')
            ext = '_rc.py'
            ext_c = '.rcc'

            # Create variables SCSS files and compile SCSS files to QSS
            logger.debug('Compiling SCSS/SASS files to QSS ...')
            create_qss(palette=palette, qss_filepath=qss_filepath)

            # creating names
            py_file_pyqt5 = '' + filename + ext
            py_file_pyqt = '' + filename + ext
            py_file_pyside = '' + filename + ext
            py_file_pyside2 = '' + filename + ext
            py_file_qtpy = '' + filename + ext
            py_file_pyqtgraph = '' + filename + ext

            # append palette used to generate this file
            used_palette = "\nfrom SerumWriter.Lib.Modern.Palette import " + palette.__name__ + "\npalette = " + palette.__name__ + "\n"

            # calling external commands
            if args.create in ['pyqt', 'pyqtgraph', 'all']:
                logger.debug("Compiling for PyQt4 ...")
                try:
                    call(['pyrcc4', '-py3', qrc_file, '-o', py_file_pyqt])
                    with open(py_file_pyqt, "a+") as f:
                        f.write(used_palette)

                except FileNotFoundError:
                    logger.debug("You must install pyrcc4")

            if args.create in ['pyqt5', 'qtpy', 'all']:
                logger.debug("Compiling for PyQt5 ...")
                try:
                    call(['pyrcc5', qrc_file, '-o', py_file_pyqt5])
                    with open(py_file_pyqt5, "a+") as f:
                        f.write(used_palette)
                except FileNotFoundError:
                    logger.debug("You must install pyrcc5")

            if args.create in ['pyside', 'all']:
                logger.debug("Compiling for PySide ...")
                try:
                    call(['pyside-rcc', '-py3', qrc_file, '-o', py_file_pyside])
                    with open(py_file_pyside, "a+") as f:
                        f.write(used_palette)
                except FileNotFoundError:
                    logger.debug("You must install pyside-rcc")

            if args.create in ['pyside2', 'all']:
                logger.debug("Compiling for PySide 2...")
                try:
                    call(['pyside2-rcc', '-py3', qrc_file, '-o', py_file_pyside2])
                    with open(py_file_pyside2, "a+") as f:
                        f.write(used_palette)
                except FileNotFoundError:
                    logger.debug("You must install pyside2-rcc")

            if args.create in ['qtpy', 'all']:
                logger.debug("Compiling for QtPy ...")
                # special case - qtpy - syntax is PyQt5
                with open(py_file_pyqt5, 'r') as file:
                    filedata = file.read()

                # replace the target string
                filedata = filedata.replace('from PyQt5', 'from qtpy')

                with open(py_file_qtpy, 'w+') as file:
                    # write the file out again
                    file.write(filedata)

                if args.create not in ['pyqt5']:
                    os.remove(py_file_pyqt5)

            if args.create in ['pyqtgraph', 'all']:
                logger.debug("Compiling for PyQtGraph ...")
                # special case - pyqtgraph - syntax is PyQt4
                with open(py_file_pyqt, 'r') as file:
                    filedata = file.read()

                # replace the target string
                filedata = filedata.replace('from PyQt4', 'from pyqtgraph.Qt')

                with open(py_file_pyqtgraph, 'w+') as file:
                    # write the file out again
                    file.write(filedata)


def main(arguments):
    """Process QRC files."""
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('--qrc_dir',
                        default=RESOURCE_PATH,
                        type=str,
                        help="QRC file directory, relative to current directory.",)
    parser.add_argument('--create',
                        default='pyqt5',
                        choices=['pyqt', 'pyqt5', 'pyside', 'pyside2', 'qtpy', 'pyqtgraph', 'qt', 'qt5', 'all'],
                        type=str,
                        help="Choose which one would be generated.")
    parser.add_argument('--watch', '-w',
                        action='store_true',
                        help="Watch for file changes.")

    args = parser.parse_args(arguments)

    run_process(args)


if __name__ == '__main__':
    # logger = OutputLogger()
    # qInstallMessageHandler(qt_message_handler)
    sys.exit(main(sys.argv[1:]))

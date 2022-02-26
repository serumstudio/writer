#!/usr/bin/env python
# -*- coding: utf-8 -*-

# Standard library imports
import importlib
import os
import sys
import inspect
import logging
import platform
import SerumWriter.Lib.Modern as Modern
import pathlib
from SerumWriter.Globals import *
from SerumWriter.Utils import relative_path

__version__ = "0.9.4"

_logger = logging.getLogger(__name__)

# Folder's path
REPO_PATH = pathlib.Path('.').absolute()

IMAGES_PATH = os.path.join(REPO_PATH, 'images')
RESOURCE_PATH = os.path.join(REPO_PATH, 'Resources')

QSS_PATH = os.path.join(RESOURCE_PATH, 'qss')
RC_PATH = os.path.join(RESOURCE_PATH, 'rc')
SVG_PATH = os.path.join(RESOURCE_PATH, 'svg')
STYLES_PATH = os.path.join(REPO_PATH, 'Themes')

BUTTONS_DARWIN_PATH = os.path.join(SVG_PATH, 'buttons_darwin')
BUTTONS_NT_PATH = os.path.join(SVG_PATH, 'buttons_nt')

# File names
QSS_FILE = 'style.qss'
QRC_FILE = QSS_FILE.replace('.qss', '.qrc')

MAIN_SCSS_FILE = 'main.scss'
STYLES_SCSS_FILE = '_styles.scss'
VARIABLES_SCSS_FILE = '_variables.scss'

# File paths
QSS_FILEPATH = os.path.join(RESOURCE_PATH, QSS_FILE)
QRC_FILEPATH = os.path.join(RESOURCE_PATH, QRC_FILE)

MAIN_SCSS_FILEPATH = os.path.join(QSS_PATH, MAIN_SCSS_FILE)
STYLES_SCSS_FILEPATH = os.path.join(QSS_PATH, STYLES_SCSS_FILE)
VARIABLES_SCSS_FILEPATH = os.path.join(QSS_PATH, VARIABLES_SCSS_FILE)

USE_DARWIN_BUTTONS = False
ALIGN_BUTTONS_LEFT = False

# Global app name
APP_NAME = None

# Path to app icon
APP_ICON_PATH = None

def palette_context(palette):
    if palette_ctx.top:
        palette_ctx.pop()

    palette_ctx.push(palette)
    return palette_ctx.top



def setAppIcon(icon_path: str):
    """Set path to app icon which will be used in titlebars"""
    Modern.APP_ICON_PATH = icon_path
   

def alignButtonsLeft():
    """Align titlebar buttons to left"""
    Modern.ALIGN_BUTTONS_LEFT = True
    _logger.info("Buttons will be aligned to left")
    

def useDarwinButtons():
    """Use darwin styled buttons everywhere in app"""
    Modern.USE_DARWIN_BUTTONS = True
    _logger.info("Darwin buttons style has been enabled")
    

def getAvailableStyles():
    """Get list of available styles"""
    return ['Dark', 'Light']


def getAvailablePalettes() -> list:
    """Get list of available palettes"""
    import Modern.Palette as source
    palettes = []
    for name, obj in inspect.getmembers(source):
        if inspect.isclass(obj) and issubclass(obj, source.BasePalette) and obj is not source.BasePalette:
            palettes.append(obj)
    return palettes



def _apply_os_patches(palette):
    """
    Apply OS-only specific stylesheet pacthes.

    Returns:
        str: stylesheet string (css).
    """
    os_fix = ""

    if platform.system().lower() == 'darwin':
        # See issue #12, #267
        os_fix = '''
        QDockWidget::title
        {{
            background-color: {color};
            text-align: center;
            height: 12px;
        }}
        QTabBar::close-button {{
            padding: 2px;
        }}
        '''.format(color=palette.COLOR_BACKGROUND_4)

    # Only open the QSS file if any patch is needed
    if os_fix:
        _logger.info("Found OS patches to be applied.")

    return os_fix


def _apply_binding_patches():
    """
    Apply binding-only specific stylesheet patches for the same OS.

    Returns:
        str: stylesheet string (css).
    """
    binding_fix = ""

    if binding_fix:
        _logger.info("Found binding patches to be applied.")

    return binding_fix


def _apply_version_patches(qt_version):
    """
    Apply version-only specific stylesheet patches for the same binding.

    Args:
        qt_version (str): Qt string version.

    Returns:
        str: stylesheet string (css).
    """
    version_fix = ""

    major, minor, patch = qt_version.split('.')
    major, minor, patch = int(major), int(minor), int(patch)

    if major == 5 and minor >= 14:
        # See issue #214
        version_fix = '''
        QMenu::item {
            padding: 4px 24px 4px 6px;
        }
        '''

    if version_fix:
        _logger.info("Found version patches to be applied.")

    return version_fix


def _apply_application_patches(palette, QCoreApplication, QPalette, QColor):
    """
    Apply application level fixes on the QPalette.

    The import names args must be passed here because the import is done
    inside the load_stylesheet() function, as PyQt5 is only imported in
    that moment for setting reasons.
    """
    # See issue #139
    color = palette.COLOR_ACCENT_3
    qcolor = QColor(color)

    # Todo: check if it is qcoreapplication indeed
    app = QCoreApplication.instance()

    _logger.info("Found application patches to be applied.")

    if app:
        app_palette = app.palette()
        app_palette.setColor(QPalette.Normal, QPalette.Link, qcolor)
        app.setPalette(app_palette)
    else:
        _logger.warning("No QCoreApplication instance found. "
                        "Application patches not applied. "
                        "You have to call load_stylesheet function after "
                        "instantiation of QApplication to take effect. ")


def _load_stylesheet(qt_api='', style=''):
    """
    Load the stylesheet based on PyQt5 abstraction layer environment variable.

    If the argument is not passed, it uses the current QT_API environment
    variable to make the imports of Qt bindings. If passed, it sets this
    variable then make the imports.

    Args:
        qt_api (str): qt binding name to set QT_API environment variable.
                      Default is ''. Possible values are pyside2,
                      pyqt5. Not case sensitive.

    Note:
        - Note that the variable QT_API is read when first imported. So,
          pay attention to the import order.
        - OS, binding and binding version number, and application specific
          patches are applied in this order.

    Returns:
        str: stylesheet string (css).
    """

    if qt_api:
        os.environ['QT_API'] = qt_api

    # Import is made after setting QT_API
    from PyQt5.QtCore import QCoreApplication, QFile, QTextStream
    from PyQt5.QtGui import QColor, QPalette
    from PyQt5.QtCore import QT_VERSION_STR as QT_VERSION

    # Search for style in styles directory
    style_dir = None

    available_styles = getAvailableStyles()
    _logger.debug(f"Available styles: {available_styles}")
    for stl in available_styles:
        if style.lower() == stl.lower():
            style_dir = stl
            break

    if style_dir is None:
        stylesheet = ""
        raise FileNotFoundError("Style " + style + " does not exists")

    # check if any style_rc was loaded before
    if "style_rc" in sys.modules:
        _logger.info("Found already imported style in sys.modules")

        # use qCleanupResources to remove all resource files
        global style_rc  # noqa
        style_rc.qCleanupResources()

        # remove imported modules
        for x in [module for module in sys.modules if module.startswith("style_rc")]:
            del sys.modules[x]
            del style_rc

        # remove path to previously imported style from sys.path
        # for stylepath in [path for path in sys.path if any(style for style in getAvailableStyles() if style in path)]:
            # sys.path.remove(stylepath)
        _logger.debug("Removed all imported styles")

    try:
        
        _logger.debug("Loading style from directory: " + style_dir)
        old_working_dir = os.getcwd()
        # set style directory
        
        package_dir = relative_path('Themes', style_dir)
        
        from pyext import RuntimeModule
        with open(os.path.join(package_dir, 'style_rc.py')) as f:
            RuntimeModule.from_string('style_rc', '', f.read())
        
        import style_rc
        palette =style_rc.palette
               

    except FileExistsError:
        raise FileNotFoundError("Missing style_rc.py file")

    
    palette_context(palette)
    _logger.info("Style resources imported successfully")

    # Thus, by importing the binary we can access the resources

    package_dir = os.path.basename(RESOURCE_PATH)
    qss_rc_path = ":" + os.path.join(package_dir, QSS_FILE)

    

    _logger.debug("Reading QSS file in: %s", qss_rc_path)

    # It gets the qss file from compiled style_rc that was import
    # not from the file QSS as we are using resources
    qss_file = QFile(qss_rc_path)
  


    if qss_file.exists():
        qss_file.open(QFile.ReadOnly | QFile.Text)
        text_stream = QTextStream(qss_file)
        stylesheet = text_stream.readAll()
        
        _logger.info("QSS file sucessfuly loaded.")
    else:
        stylesheet = ""
        # Todo: check this raise type and add to docs
        raise FileNotFoundError("Unable to find QSS file '{}' "
                                "in resources.".format(qss_rc_path))

    _logger.debug("Checking patches for being applied.")

    # Todo: check execution order for these functions
    # 1. Apply OS specific patches
    stylesheet += _apply_os_patches(palette)

    # 2. Apply binding specific patches
    stylesheet += _apply_binding_patches()

    # 3. Apply binding version specific patches
    stylesheet += _apply_version_patches(QT_VERSION)

    # 4. Apply palette fix. See issue #139
    _apply_application_patches(palette, QCoreApplication, QPalette, QColor)

    return stylesheet


def load_stylesheet(qt_api="", style='dark'):
    """
    Load the stylesheet. Takes care of importing the rc module.

    Args:
        qt_api (str): Qt binding name to set QT_API environment variable.
                      Default is '', i.e PyQt5 the default PyQt5 binding.
                      Possible values are pyside2, pyqt5.
                      Not case sensitive.

        style (str): Style to use. Default is 'darkblue'

    Returns:
        str: the stylesheet string.
    """

    stylesheet = ""

    if qt_api:
        stylesheet = _load_stylesheet(qt_api=qt_api, style=style)

    else:
        stylesheet = _load_stylesheet(qt_api='pyqt5', style=style)

    return stylesheet


def load_stylesheet_pyside2(style='dark'):
    """
    Load the stylesheet for use in a PySide2 application.

    Returns:
        str: the stylesheet string.
    """
    return _load_stylesheet(qt_api='pyside2', style=style)


def load_stylesheet_pyqt5(style='dark'):
    """
    Load the stylesheet for use in a PyQt5 application.

    Returns:
        str: the stylesheet string.
    """
    return _load_stylesheet(qt_api='pyqt5', style=style)

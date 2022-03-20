
# Copyright (c) 2022 Serum

# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import os
import SerumWriter.Properties as Properties
from SerumWriter.Lib.Modern import load_stylesheet
from SerumWriter.Globals import app_ctx
from SerumWriter.Views.MainWindow import Main
import sys
import argparse
import pathlib

from PyQt5.QtWidgets import (
    QApplication,

)
from PyQt5.QtGui import (
    QFontDatabase,
)
from PyQt5.QtCore import (
    QTimer,
    
)
from SerumWriter.Components.Splashscreen import SplashScreen
from SerumWriter.Plugins.Manager import create_plugin_folder

#: bypass module error (pyinstaller)

    

def load_module_path():
    p = pathlib.Path().home() / '.serum'
    mod = p / 'Modules'
    if not mod.exists():
        os.mkdir(mod.absolute())
    elif mod.exists() and mod.is_file():
        os.remove(mod.absolute())
        os.mkdir(mod.absolute())
    

    sys.path.append(str(mod.absolute()))


def set_stylesheet(app: 'QApplication', default_theme: str = 'dark'):

    if default_theme:

        app.setStyleSheet(load_stylesheet(style=default_theme))
        Properties.Settings().theme = default_theme.lower()
        return     

    theme = Properties.Settings().theme
    
    if not theme:
        Properties.Settings().theme = default_theme.lower()
        theme = default_theme.lower()

    app.setStyleSheet(load_stylesheet(style=theme))
    return

def app_context():
    app = QApplication(sys.argv)
    if app_ctx.top:
        app_ctx.pop()
    
    
    app_ctx.push(app)
    return app

def load_fonts():
    QFontDatabase.addApplicationFont(":Resources/fonts/FiraMono-Regular.ttf")
    QFontDatabase.addApplicationFont(":Resources/FiraCode-Regualr.ttf")

def show_window(w, s):
    print('MainWindow initialized')
    w.show()
    s.close()
    

def main(args):
    
    create_plugin_folder()
    load_module_path()
    args = args[1:]
    
    parser = argparse.ArgumentParser()
    parser.add_argument('file', nargs='?')
    parser.add_argument('-md', '--markdown', action='store_true')
    args = parser.parse_args(args)
    
    app = app_context()
    app.setStyle('Fusion')
  
    splash = SplashScreen()


    set_stylesheet(app)
    load_fonts()

    
    if args.file:
        file = pathlib.Path(args.file)
        
        if file.exists() and file.is_file():
            Properties.Settings().filename = str(file.absolute())
           
    
    
    w = Main()
    QTimer.singleShot(2500, lambda: show_window(w, splash))
    
    app.exec_()

if __name__ == '__main__':
    main(sys.argv)

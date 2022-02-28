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
import pathlib
from SerumWriter.Utils.Local import (
    LocalProxy,
    LocalStack
)
import typing as t

if t.TYPE_CHECKING:
    from SerumWriter.Lib.Modern.Palette import BasePalette
    from PyQt5.QtWidgets import QApplication
    from SerumWriter.Components.Editor import Editor

BASE_DIR = pathlib.Path('.')
RESOURCES_PATH = str((BASE_DIR / 'Resources').absolute())

BUTTONS_PATH = os.path.join(RESOURCES_PATH, 'svg', 'buttons')
RC_PATH = str((BASE_DIR / 'rc').absolute())

def look_up_palette():
    top = palette_ctx.top

    if not top:
        raise RuntimeError('Palette is used outside the app')
    return top

def look_up_app():
    top = app_ctx.top
    if not top:
        raise RuntimeError('App Instance is used outside the app')

    return top

def look_up_editor():
    top = editor_ctx.top
    if not top:
        raise RuntimeError('Editor Instance is used outside the app')

    return top

def look_up_resouce_module():
    top = res_module_ctx.top

    if not top:
        raise RuntimeError('')
    
    return top

__version__ = '0.0.2'
editor_ctx = LocalStack()
res_module_ctx = LocalStack()
palette_ctx = LocalStack()
app_ctx = LocalStack()
palette: 'BasePalette' = LocalProxy(look_up_palette)
app: 'QApplication' = LocalProxy(look_up_app)
editor: 'Editor' = LocalProxy(look_up_editor)
resource = LocalProxy(look_up_resouce_module)
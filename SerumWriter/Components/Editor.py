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
from PyQt5.QtWidgets import (
    QTextEdit,
    QFileDialog,
    QWidget,
    QHBoxLayout,
    QLabel,
    QLineEdit,
    QPushButton
)

from PyQt5.QtGui import (
    QTextBlockFormat,
    QTextFormat,
    QColor,
    QFont,
    QKeyEvent,
    QTextCursor,
    QPainter

)
from SerumWriter.Components.Dialog import MaskDialog
from PyQt5.QtCore import (
    pyqtSignal as Signal,
    Qt, 
    QTimer,
    QPropertyAnimation,
    QPoint,
    QEasingCurve,
    QMimeData
)
from SerumWriter.Globals import palette
from markdown import markdown
from SerumWriter.Lib.Highlighter import SpellCheckWrapper, SyntaxHighlighter
import SerumWriter.Properties as Properties
import pathlib

from SerumWriter.Plugins import EditorPlugin
from SerumWriter.Plugins.Manager import (
    PluginManager
)

class Find(QWidget):
    """
    A Widget used for finding strings (CTRL + F)
    The parent widget should be the `Main` instannce
    """

    def __init__(self, editor: 'Editor', parent=None):
        super().__init__(parent=parent)
        self.editor = editor

        self.setObjectName('Find')
        self._layout = QHBoxLayout()
        self._layout.setContentsMargins(0,0,0,0)
        
        self.setLayout(self._layout)
        self.init_widgets()

    def init_widgets(self):
        
        self.animIn = QPropertyAnimation(self, b'geometry', duration=500, easingCurve=QEasingCurve.OutCubic)
        self.animIn.setPropertyName(b'pos')
        self.animOut = QPropertyAnimation(self, b'geometry', duration=500, easingCurve=QEasingCurve.Type.OutCubic)
        self.animOut.setPropertyName(b'pos')

        self.find_edit = QLineEdit()
        self.find_edit.textChanged.connect(self.textChanged)
        self.find_edit.setPlaceholderText('Find')
        self.find_edit.setFixedWidth(160)
       

        self._layout.addWidget(self.find_edit) 


    def textChanged(self):
        words = self.find_edit.text()
        if not self.editor.find(words):
            # no match found, move the cursor to the beginning of the
            # document and start the search once again
            cursor = self.editor.textCursor()
            cursor.setPosition(0)
            self.editor.setTextCursor(cursor)
            self.editor.find(words)

class Preview(QTextEdit):

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFont(QFont('Segoe UI'))
        self.setViewportMargins(40,40,40,40)
        self._cursor = self.textCursor()
        self.setReadOnly(True)
        self.setObjectName('Preview')
   
        
    def setMarkdownOnMargin(self, md: str):
        self.clear()
        self._cursor.insertHtml(markdown(md))
        

class Editor(QTextEdit):
    cursor_visible: bool = True
    textChangedEvent = Signal(str)
    fileNameChanged = Signal(str)
    
    surround_keys = [
        Qt.Key.Key_Underscore,
		Qt.Key.Key_Asterisk,
    ]
    __placeholder = None
    __filename: str = None
    _saved: bool = False
    _show_status = Signal(str)
    _current_text: str = None
    __extension = ''
    __name = None
    __word_list_path = "wordlist"

    def __init__(self, parent=None, **options):
        super().__init__(parent=parent)
        self._parent = parent
        self._focus_mode = options.get('focus', True)
        self.__placeholder = options.get('placeholder', '')
        self.spell_checking = options.get('spell_checking', False)
        self._properties = Properties.Settings()
        self.plugin_manager = PluginManager
        
        if self.spell_checking:
            spell_checker = SpellCheckWrapper(self.get_words(), self.addToDictionary)
        else:
            spell_checker = None

        self.highlighter = SyntaxHighlighter(
            self.document(),
            docType=self.getFileExtension(),
            palette=palette,
            spell_checker=spell_checker
        )

        if hasattr(self, "speller"):
            self.spellchecker.setSpeller(self.speller)

        self.plugin_manager.setCategoriesFilter({'EditorPlugin': EditorPlugin})
        try:
            self.plugin_manager.collectPlugins()
        except Exception as e:
            #: Load plugin error
            print(e)

        self._parent.changed_style.connect(self.init_kwargs)

        self.setFont(QFont('Fira Mono'))
        self.setAcceptRichText(False)   
        self.setViewportMargins(40,40,40,40)
        self.setLineHeight()
    
        self.init_kwargs()
        self.textChanged.connect(lambda: self.textChangedEvent.emit(self.toPlainText()))
        self.textChangedEvent.connect(self.text_changed)
        self.__init_formats()
        #: force set focus
        QTimer.singleShot(0, self.setFocus)

        #: Cursor animation
        timer = QTimer(self)
        timer.timeout.connect(self.cursorTime)
        timer.start(600)
        
        
        self.continue_dialog = MaskDialog(
            'Serum Writer', 
            'Would you like to continue the operation without saving? This may lost all the progress',
            self._parent
        )
        self.continue_dialog.hide()

        self.exit_dialog = MaskDialog(
            'Serum Writer', 
            'Would you like to exit the app without saving? This may lost all the progress',
            self._parent
        )

        
        
        self.exit_dialog.hide()
        

        if self._properties.filename != None \
            and pathlib.Path(self._properties.filename).exists():

            self._open(self._properties.filename)
        else:
            self.clear()

    def run_plugins(self):

        for plugin in self.plugin_manager.getAllPlugins():
            po = plugin.plugin_object
            
            try:
                po.init(self, self._parent)
            except AttributeError:
                pass
            
            try:
                po.run()
            except AttributeError:
                pass

    def get_words(self):
        if not os.path.exists(self.__word_list_path):
            f = open(self.__word_list_path, 'w')
            f.close()
            return []

        with open(self.__word_list_path, 'r') as f:
            world_list = [line.strip() for line in f.readlines()]
        
        return world_list
    
    def addToDictionary(self, word):
        with open(self.__word_list_path, 'a') as f:
            f.write('\n'+word)

    def clear(self) -> None:
        QTextEdit.clear(self)
        self.setLineHeight()

    def setFileName(self, f: str) -> str:
        self.__filename = f
        return self.__filename

    def fileExtension(self):
        return self.__extension


    def getFileExtension(self):
        _dict = {
            '.md': 'Markdown',
            '.rst': 'reStructuredText',
            '.html': 'html',
            '.textile': 'Textile'

        }
        
        if self.fileExtension():
            try:
                return _dict.get(self.fileExtension(), 'Markdown')
            except KeyError:
                return "Markdown"

        elif self.fileName():
            try:
                return _dict.get(pathlib.Path(self.fileName()).suffix, 'Markdown')
            except KeyError:
                return "Markdown"

        elif not self.fileName() and not self.fileExtension():
            return 'Markdown'
            


    def fileName(self, name: bool=False):
        if name:
            return self.__name

        return self.__filename

    def focusMode(self):
        return self._focus_mode
    
    def setFocusMode(self, v: bool):
        self._focus_mode = v
        return self._focus_mode

    def text_changed(self, text: str):
        self._saved = False
        

        if self.fileName() != None and self._current_text != text:
            self._show_status.emit('*  %s' % (self.__name)) 
    



    def highlightCurrentLine(self, color):
        if self._focus_mode:
            selection = QTextEdit.ExtraSelection()
            selection.format.setForeground(QColor(color))
            selection.format.setProperty(QTextFormat.Property.FullWidthSelection, True)
            selection.cursor = self.textCursor()
            selection.cursor.clearSelection()
            selections = [selection]
            self.setExtraSelections(selections)
        else:
            self.setStyleSheet('color: {}'.format(palette.COLOR_TEXT_2))
        
    

    def keyPressEvent(self, e: QKeyEvent) -> None:
        key = e.key()
        cursor = self.textCursor()

        
        if cursor.selectedText() and self.__is_surround_key(key):
            self.__surround_text(cursor, e.text(), selection=True)

        elif self.__is_surround_key(key):
            self.__surround_text(cursor, e.text())

        return super().keyPressEvent(e)

    def __surround_text(self, cursor: QTextCursor, key:str='', selection=False, selected_text: str=None):
        if selection:
            
            if selected_text:
                text = selected_text
            else:
                text = cursor.selectedText()
            
            cursor.insertText(key + text)
            
            return text
            
        pos = cursor.position()
        self.insertPlainText(key)
        cursor.setPosition(pos)
        self.setTextCursor(cursor)
        return key

    def __is_surround_key(self, key):
        return key in self.surround_keys
    
    def init_kwargs(self):
        
        self.setCursorWidth(2)
        if self._focus_mode:
            fg = palette.COLOR_TEXT_2
            lightness = QColor(fg).lightness()
            if lightness > 150:
                color = QColor(fg).darker(200).name()
            else:
                color = QColor(fg).lighter(300).name()

            self.setStyleSheet('color: {};'.format(color))
            self.cursorPositionChanged.connect(
                lambda: self.highlightCurrentLine(fg)
            )
            #E0E1E3
            #707071

            #3e3c38 #1f1e1c
            

        if self.__placeholder:
            self.setPlaceholderText(self.__placeholder)
        else:
            self.setPlaceholderText('')

    def paintEvent(self, event):
        # Change cursor color 
        QTextEdit.paintEvent(self, event)
        if self.hasFocus():
            if self.cursor_visible:
                
                rect = self.cursorRect(self.textCursor())
                painter = QPainter(self.viewport())
                painter.fillRect(rect, QColor(palette.COLOR_ACCENT_4))
            elif not self.cursor_visible:
                
                rect = self.cursorRect(self.textCursor())
                painter = QPainter(self.viewport())
                painter.fillRect(rect, QColor(palette.COLOR_BACKGROUND_1))        

    def setLineHeight(self, height: int=12):
        bf = self.textCursor().blockFormat()
        bf.setLineHeight(height, QTextBlockFormat.LineHeightTypes.LineDistanceHeight)
        self.textCursor().setBlockFormat(bf)
        

    def setPlainText(self, text: str) -> str:
        self.clear()
        self.setLineHeight()
        self.textCursor().insertText(text)
        return text
        
    def cursorTime(self): 
        
        if self.cursor_visible:
            self.cursor_visible = False
        else:
            self.cursor_visible = True
    
    def __init_formats(self):
        self.setTabStopWidth(40)

    def save(self):
        if not self.fileName():
            self.saveAs()
        else:
            with open(self.fileName(), 'w') as f:
    
                f.write(self.toPlainText())

        
        self._saved = True
        if self.fileName():
            self.__name = pathlib.Path(self.fileName()).name
        
        if self.fileName() != None and self._saved:
            self._show_status.emit('%s' % (self.__name))

        self._current_text = self.toPlainText()
        self.updateProperties()
        
        self.highlighter.docType = self.getFileExtension()
        self.highlighter.rehighlight()

    def saveAs(self):
        file = QFileDialog.getSaveFileName(
            self, 
            'Save File', 
            os.getcwd(), 
            "Markdown (*.md);;Text (*.txt);;All Files (*)"
        )[0]
        self.__extension = pathlib.Path(file).suffix
        if file:
            self.setFileName(file)
            self.fileNameChanged.emit(self.fileName())
            if self.fileName():
                self.__name = pathlib.Path(self.fileName()).name
        
            if self.fileName() != None and self._saved:
                self._show_status.emit('%s' % (self.__name))
            
            
            with open(self.fileName(), 'w') as f:
                f.write(self.toPlainText())

            self.updateProperties()

        self.highlighter.docType = self.getFileExtension()
        self.highlighter.rehighlight()

    def save_and_clear(self):
        self.save()
        self.clear()

    def hide_and_clear(self):
        self.hide()
        self.clear()

    def new(self):
        
        if self._current_text != self.toPlainText():
            #: Warning
            self.continue_dialog.yesSignal.connect(self.clear)
            self.continue_dialog.exec_()
            if self.toPlainText() == '':
                self.setFileName(None)

        elif self._current_text == self.toPlainText():
            self.setFileName(None)
            self.clear()

        elif self.toPlainText() == '':
            self.setFileName(None)
            self.clear()

        else:
            self.setFileName(None)
            self.clear()
        
    def close_file(self):
        text = self.toPlainText()
        def close_and_clear():
            self.setFileName(None)
            self._show_status.emit(' ')
            self.clear()

        if self._current_text != text and text != '':
            self.continue_dialog.yesSignal.connect(close_and_clear)
            self.continue_dialog.exec_()
        else:
            close_and_clear()

        self.updateProperties()
        

    def _open(self, file: str):
        self.setFileName(file)
        self.__name = pathlib.Path(self.fileName()).name
        self.fileNameChanged.emit(self.fileName())
        

        with open(self.fileName(), 'r') as f:
            data = f.read()

        self._current_text = data
        self._show_status.emit('%s' % (self.__name))
        return self.setPlainText(data)        
    
    
    def open(self):
        file = QFileDialog.getOpenFileName(
            self,
            'Open File',
            os.getcwd(),
            'Markdown (*.md);;Text (*.txt);;Serum Notes (*.snote);;All Files (*)'
        )[0]
        self.__extension = pathlib.Path(file).suffix
        text = self.toPlainText()
        
        if file:
            if self._current_text != text and text != '':
                self.continue_dialog.yesSignal.connect(lambda: self._open(file))
                self.continue_dialog.exec_()
                self.updateProperties()
                
                
            else:
                self._open(file)
                self.updateProperties()

        self.highlighter.docType = self.getFileExtension()
        self.highlighter.rehighlight()

    def insertHeader(self, level: int=1):
        self.textCursor().insertText('{header} '.format(header='#'*level))

    def insertQuoteBlock(self):
        self.textCursor().insertText('> ')
    
    def insertCodeBlock(self):
        pass

    def insertBold(self):
        key = "**"        
        cursor = self.textCursor()
        selected_text = self.textCursor().selectedText()
        if selected_text:
            selection = True
        else:
            selection = False


        self.insertPlainText(key)
        if not selection:
            self.__surround_text(
                cursor, 
                key, 
                False
            )
        else:
            cursor.insertText(selected_text + key)

    def insertItalic(self):
        key = "*"
        cursor = self.textCursor()
        selected_text = self.textCursor().selectedText()
        if selected_text:
            selection = True
        else:
            selection = False


        self.insertPlainText(key)
        if not selection:
            self.__surround_text(
                cursor, 
                key, 
                False
            )
        else:
            cursor.insertText(selected_text + key)

    def insertImage(self):
        cursor = self.textCursor()
        self.insertPlainText('![Image Name](')
        start = cursor.position()
        self.insertPlainText('Image Url')
        end = cursor.position()
        self.insertPlainText(')')

        cursor.setPosition(start)
        cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)

    def insertList(self, ordered: bool=False):
        cursor = self.textCursor()
        cursor.insertText('- ')
        
        

    def insertLink(self):
        cursor = self.textCursor()
        self.insertPlainText('[Link Title](')
        start = cursor.position()
        self.insertPlainText('Link')
        end = cursor.position()
        self.insertPlainText(')')

        cursor.setPosition(start)
        cursor.setPosition(end, cursor.MoveMode.KeepAnchor)
        self.setTextCursor(cursor)


    def updateProperties(self):
        
        if self.fileName():
            self._properties.filename = self.fileName()

            
        elif self.fileName() == None:
            self._properties.filename = None
        else:
            self.setFileName(self._properties.filename)

    def insertFromMimeData(self, source: QMimeData) -> None:
        return super().insertFromMimeData(source)

    def toRawHtml(self):
        return markdown(self.toPlainText())
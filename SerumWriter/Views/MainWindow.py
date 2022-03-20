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

from SerumWriter.Components.Window import FramelessWindow
from SerumWriter.Components.Statusbar import Statusbar
from SerumWriter.Globals import (
    palette,
    app,
    __version__
)
import os
from PyQt5.QtWidgets import (
    QDesktopWidget,
    QMenu,
    QWidget,
    QHBoxLayout,
    QShortcut,
    QLabel,
    QGraphicsOpacityEffect,
    QFileDialog
)
from PyQt5.QtGui import (
    QKeySequence,
    QIcon
)
from PyQt5.QtCore import (
    QPropertyAnimation,
    pyqtSignal
)
from SerumWriter.Components.Dialog import (
    MaskDialog, 
    Preference
)
from SerumWriter.Components.Editor import (
    Editor, 
    Preview,
    Find
)
from SerumWriter.Components.Splashscreen import res
from SerumWriter.Lib.Builder import PDFBuilder
from SerumWriter.Lib.Highlighter import SpellCheckWrapper
from SerumWriter.Lib.Modern import load_stylesheet
from SerumWriter.Utils import word_count
import SerumWriter.Properties as Properties

import typing as t
if t.TYPE_CHECKING:
    from PyQt5.QtGui import (
        QResizeEvent,
        QShowEvent
    )
    from PyQt5.QtCore import (
        QPoint
    )

import webbrowser

class Menu(QMenu):
    _position: 'QPoint' = None
    def __init__(self, title: str, parent=None):
        super().__init__(title=title, parent=parent)
        self._position = self.pos()
        
    def showEvent(self, e: 'QShowEvent') -> None:
        return super().showEvent(e)

class Main(FramelessWindow):
    __word_count = None
    __status_label = None
    changed_style = pyqtSignal()
    template_name: str = 'Serum Writer'
    export_dialog = None
    _spell_check = Properties.Settings().spell_check

    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/image/logo.png'))
        self.properties = Properties.Settings()
        self._titlebar = self.titlebar()

        if self.properties.height and self.properties.width:
            self.setMinimumSize(
                self.properties.width,
                self.properties.height
            )
        else:
            self.setMinimumSize(820, 520)


        self.center()
        self.setWindowTitle('Serum Writer')
            

        self._titlebar.show_event.connect(self.edit_titlebar_border_bottom)
        self._hlayout = QHBoxLayout()
        self._hlayout.setContentsMargins(0,0,0,0)
        
        self.main_menu = Menu('main', self._titlebar)
        self.setStyleSheet('''
        QMenu::separator {
            height: 1px;
            background-color: #282828;
        }
        ''')
        #: File Menu
        self.file_menu = self.main_menu.addMenu("File")
        self.new_file = self.file_menu.addAction('New File')
        
        self.open_file = self.file_menu.addAction('Open File')
        
        self.close_file = self.file_menu.addAction('Close File')
        
        self.save_file = self.file_menu.addAction('Save File')
        
        self.save_file_as = self.file_menu.addAction('Save File As')
        self.file_menu.addSeparator()
        
        self.spell_checking = self.file_menu.addAction('Spell Checking')
        self.spell_checking.setCheckable(True)
        
        if self._spell_check:
            self.spell_checking.setChecked(True)

        # self.pref = self.file_menu.addAction('Preferences')

        self.export_menu = self.file_menu.addMenu('Export')
        self.export_pdf = self.export_menu.addAction('Export to PDF')

        self.menu_exit = self.file_menu.addAction('Exit')
        
        #: Edit Menu
        self.edit_menu = self.main_menu.addMenu("Edit")
        self.undo_edit = self.edit_menu.addAction('Undo')
        self.redo_edit = self.edit_menu.addAction('Redo')
        
        self.edit_menu.addSeparator()
        
        self.cut_edit = self.edit_menu.addAction('Cut')
        
        self.copy_edit = self.edit_menu.addAction('Copy')
        
        self.paste_edit = self.edit_menu.addAction('Paste')
        
        self.edit_menu.addSeparator()
        
        edit_insert = self.edit_menu.addMenu('Insert')
        header_insert = edit_insert.addMenu('Headers')
        self.insert_header_1 = header_insert.addAction('H1 (Header 1)')
        self.insert_header_2 = header_insert.addAction('H2 (Header 2)')
        self.insert_header_3 = header_insert.addAction('H3 (Header 3)')
        self.insert_header_4 = header_insert.addAction('H4 (Header 4)')
        self.insert_header_5 = header_insert.addAction('H5 (Header 5)')
        self.insert_header_6 = header_insert.addAction('H6 (Header 6)')
    
        edit_insert.addSeparator()
    
        self.insert_bold = edit_insert.addAction('Bold')
        self.insert_italic = edit_insert.addAction('Italic')

        edit_insert.addSeparator()
        self.insert_code_block = edit_insert.addAction('Code Block')
        self.insert_block_quote = edit_insert.addAction('Block Quote')
        
        edit_insert.addSeparator()
        self.insert_image = edit_insert.addAction('Image')
        self.insert_link = edit_insert.addAction('Link')
        
        
        #: View Menu
        view = self.main_menu.addMenu('View')
        self.preview_menu = view.addAction('Preview Mode')
        self.preview_menu.setCheckable(True)

        change_theme = self.main_menu.addMenu('Theme')
        self._light_theme = change_theme.addAction('Light')
        self._light_theme.setCheckable(True)
        self._dark_theme = change_theme.addAction('Dark')
        self._dark_theme.setCheckable(True)

        _help = self.main_menu.addMenu('Help')
        about = _help.addAction('About')
        about.triggered.connect(self.show_about_dialog)

        if self.properties.theme == 'dark':
            self._dark_theme.setChecked(True)
        else:
            self._light_theme.setChecked(True)
        
        self._light_theme.triggered.connect(lambda: self.change_theme('light'))
        self._dark_theme.triggered.connect(lambda: self.change_theme('dark'))

        self._titlebar.settings_btn.setMenu(self.main_menu)
        self._titlebar.showSettingsButton()

        
        self.editor = Editor(self, spell_checking=self._spell_check)
        if self.editor.toPlainText() != '':
            self.__word_count = word_count(self.editor.toPlainText())
        self.preview = Preview()


        
        self.editor.textChangedEvent.connect(self.typing_event)
        self.editor._show_status.connect(self.show_status)

        self._hlayout.addSpacing(40)
        self._hlayout.addWidget(self.editor)
        
        if not self.properties.preview: self.preview.hide()
        self._hlayout.addWidget(self.preview)

        self.__init_shortcuts()
        self.addContentLayout(self._hlayout)
    
        if not self.preview.isHidden():
            self.edit_titlebar_border_bottom()
        

        
        #: Menu signals
        self.new_file.triggered.connect(self.editor.new)
        self.open_file.triggered.connect(self._open_file)
        self.close_file.triggered.connect(self.editor.close_file)
        self.save_file.triggered.connect(self._save_file)
        self.save_file_as.triggered.connect(self.save_as)
        
        # self.pref.triggered.connect(self.show_pref)
        self.export_pdf.triggered.connect(self._export_pdf)
        self.spell_checking.triggered.connect(self.add_spell_checking)
        self.menu_exit.triggered.connect(self.close)

        #: Edit Signals
        self.insert_header_1.triggered.connect(lambda: self.editor.insertHeader(1))
        self.insert_header_2.triggered.connect(lambda: self.editor.insertHeader(2))
        self.insert_header_3.triggered.connect(lambda: self.editor.insertHeader(3))
        self.insert_header_4.triggered.connect(lambda: self.editor.insertHeader(4))
        self.insert_header_5.triggered.connect(lambda: self.editor.insertHeader(5))
        self.insert_header_6.triggered.connect(lambda: self.editor.insertHeader(6))
        
        self.insert_bold.triggered.connect(self.editor.insertBold)
        self.insert_italic.triggered.connect(self.editor.insertItalic)

        self.insert_code_block.triggered.connect(self.editor.insertCodeBlock)
        self.insert_block_quote.triggered.connect(self.editor.insertQuoteBlock)

        self.insert_image.triggered.connect(self.editor.insertImage)
        self.insert_link.triggered.connect(self.editor.insertLink)

        #: View
        self.preview_menu.triggered.connect(self.__preview_show)

        
        #: Run editor plugins
        self.editor.run_plugins()
  
        
        #: Add find 
        self._find = Find(self.editor, self)
        self._find.hide()

        self.about_dialog = MaskDialog(
            'Serum Writer', 
            'Next generation - elegant text editor built for your needs.\n\nVersion: {version}.\nDeveloped By: Zenqi\nGithub: @zxnqi\n\nArtwork by: ori toor (https://oritoor.com)'.format(
                version=__version__
            ),
            self
        )
        self.about_dialog.hide()

        #: Statusbar
        self.status_bar = Statusbar(self)
        self.__status_bar()
        self.__update_statusbar()

    def add_spell_checking(self):
        
        if self.spell_checking.isChecked():
            self.editor.highlighter.speller = SpellCheckWrapper(
                self.editor.get_words(),
                self.editor.addToDictionary
            )
            self.properties.spell_check = True
            
            return 

    
        self.editor.highlighter.speller = None
        self.properties.spell_check = False

        

    def show_about_dialog(self):
        self.about_dialog.yesButton.setText('Ok')
        self.about_dialog.exec_()

    def show_pref(self):
        dialog = Preference(self)
        dialog.show()

    def change_theme(self, theme: str='dark'):

        self.properties.theme = theme
        app.setStyleSheet(load_stylesheet(style=theme))
        self.changed_style.emit()
        if theme == 'dark':
            self._dark_theme.setChecked(True)
            self._light_theme.setChecked(False)
        else:
            self._light_theme.setChecked(True)
            self._dark_theme.setChecked(False)

    def __init_shortcuts(self):
        QShortcut(QKeySequence('Ctrl+,'), self)\
            .activated.connect(self.show_pref)

        QShortcut(QKeySequence('Ctrl+R'), self)\
            .activated.connect(self.__preview_show)

        QShortcut(QKeySequence('Ctrl+N'), self)\
            .activated.connect(self.editor.new)

        QShortcut(QKeySequence('Ctrl+O'), self)\
            .activated.connect(self._open_file)

        QShortcut(QKeySequence('Ctrl+S'), self)\
            .activated.connect(self._save_file)
        
        QShortcut(QKeySequence('Ctrl+Shift+S'), self)\
            .activated.connect(self.save_as)

        QShortcut(QKeySequence('Ctrl+Shift+O'), self)\
            .activated.connect(self.editor.close_file)

        #: Edit
        QShortcut(QKeySequence('Ctrl+Shift+1'), self)\
            .activated.connect(lambda: self.editor.insertHeader(1))

        QShortcut(QKeySequence('Ctrl+Shift+2'), self)\
            .activated.connect(lambda: self.editor.insertHeader(2))

        QShortcut(QKeySequence('Ctrl+Shift+3'), self)\
            .activated.connect(lambda: self.editor.insertHeader(3))

        QShortcut(QKeySequence('Ctrl+Shift+4'), self)\
            .activated.connect(lambda: self.editor.insertHeader(4))

        QShortcut(QKeySequence('Ctrl+Shift+5'), self)\
            .activated.connect(lambda: self.editor.insertHeader(5))

        QShortcut(QKeySequence('Ctrl+Shift+6'), self)\
            .activated.connect(lambda: self.editor.insertHeader(6))

        QShortcut(QKeySequence('Ctrl+B'), self)\
            .activated.connect(self.editor.insertBold)

        QShortcut(QKeySequence('Ctrl+Shift+I'), self)\
            .activated.connect(self.editor.insertItalic)
        
        QShortcut(QKeySequence('Ctrl+I'), self)\
            .activated.connect(self.editor.insertImage)

        QShortcut(QKeySequence('Ctrl+Shift+H'), self)\
            .activated.connect(self.editor.insertLink)
    
        QShortcut(QKeySequence('Ctrl+Shift+L'), self)\
            .activated.connect(self.editor.insertList)
        
        QShortcut(QKeySequence('Ctrl+Shift+Q'), self)\
            .activated.connect(self.editor.insertQuoteBlock)

        QShortcut(QKeySequence('Ctrl+F'), self)\
            .activated.connect(self.show_find)

        QShortcut(QKeySequence('Ctrl+Shift+B'), self)\
            .activated.connect(self._export_pdf)

    def show_find(self):
        if self._find.isHidden():
            self._find.show()
            self._find.setFocus()
        else:
            self._find.hide()
        
        self._find.setFocus()

    def _save_file(self):
        self.editor.save()
        

    
    def _open_file(self):
        self.editor.open()
   
        
        
    def save_as(self):
        self.editor.saveAs()
  
    def _export_pdf(self):
        builder = PDFBuilder(self.editor.toRawHtml(), self.template_name)
        file = QFileDialog.getSaveFileName(
            self, 
            'Export to PDF', 
            os.getcwd(), 
            "PDF (*.pdf);;All Files (*)"
        )[0]

        builder.export(file)
        print('Done exporting: %s' % (file))
        self.export_dialog = MaskDialog(
            'Serum Writer',
            'Succesfully exported to PDF: %s' % (file),
            self
        )
        self.export_dialog.yesButton.setText('Open')
        self.export_dialog.yesButton.clicked.connect(lambda: webbrowser.open_new_tab(file))
        self.export_dialog.exec_()

    def closeEvent(self, e):
        self.properties.height = self.height()
        self.properties.width = self.width()

        text = self.editor.toPlainText()
        
        if self.editor._current_text != text and text != '':
            self.editor.exit_dialog.yesSignal.connect(e.accept)
            self.editor.exit_dialog.cancelSignal.connect(e.ignore)
            self.editor.exit_dialog.exec_()
        

    
    def resizeEvent(self, e: 'QResizeEvent'):
        
        if self.export_dialog:
            self.export_dialog.init_widget(
                e.size().width(),
                e.size().height()
            )
            if not self.export_dialog.isHidden():
                self.export_dialog.init_widget()

        self.editor.continue_dialog.init_widget(
            e.size().width(), 
            e.size().height()
        )
        self.editor.exit_dialog.init_widget(
            e.size().width(), 
            e.size().height()
        )
        self.about_dialog.init_widget(
            e.size().width(), 
            e.size().height()
        )
        self._find.move(
            70,
            e.size().height()
        )
        if not self.editor.continue_dialog.isHidden():
            self.editor.continue_dialog.init_widget()

        if not self.editor.exit_dialog.isHidden():
            self.editor.exit_dialog.init_widget()

        if not self.about_dialog.isHidden():
            self.about_dialog.init_widget()
        
        self._find.move(
            70,
            e.size().height() - 30
        )
        self.status_bar.move(
            e.size().width() - 200,
            e.size().height() - 30
        )
        return super().resizeEvent(e)

    

    def edit_titlebar_border_bottom(self):
        if not self.preview.isHidden():
            self._titlebar.bottomBorderColor()
        else:
            self._titlebar.bottomBorderColor(show=False)

    def center(self):
        fm = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fm.moveCenter(cp)
        self.move(fm.topLeft())

    def show_status(self, name: str):
      
        self.setWindowTitle('Serum Writer - %s' % (name))
        self.__status_label = name
        self.__update_statusbar()

    def fade(self, widget):
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.start()

    def unfade(self, widget):
        self.effect = QGraphicsOpacityEffect()
        widget.setGraphicsEffect(self.effect)

        self.animation = QPropertyAnimation(self.effect, b"opacity")
        self.animation.setDuration(1000)
        self.animation.setStartValue(0)
        self.animation.setEndValue(1)
        self.animation.start()


    
    def __status_bar(self) -> QWidget:
        #: There is some errror subclassing widget so i;ll create the 
        #: status bar in the main window
        self.wordcount_label = QLabel()
        self.wordcount_label.setText('0 Word')
        
        self.status_label = QLabel()
        self.status_label.setObjectName('statusLabel')

        if self.editor.fileName(name=True):
            self.status_label.setText(self.editor.fileName(name=True))

        self.status_bar.addWidget(self.wordcount_label)
        self.status_bar.addWidget(self.status_label)

    def __preview_show(self):

        if self.preview.isHidden():
            self.preview_menu.setChecked(True)
            self.preview.show()
            self.properties.preview = True

        else:
            self.preview_menu.setChecked(False)
            self.preview.hide()
            self.properties.preview = False


       
    def __update_statusbar(self):

        if self.__word_count == 0:
            self.wordcount_label.setText('0 Word')
        elif self.__word_count:
            self.wordcount_label.setText('{} Words'.format(self.__word_count))

        if self.__status_label:
            if self.__status_label == '':
                
                self.unfade(self.status_label)
            self.status_label.setText(self.__status_label)

    def typing_event(self, text: str):
        self.__word_count = word_count(text)
        
        self.__update_statusbar()
        self.preview.setMarkdownOnMargin(text)
        self._titlebar.animation(animOut=True)
        

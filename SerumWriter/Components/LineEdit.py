
from PyQt5.QtWidgets import (
    QLineEdit,
    QGraphicsDropShadowEffect,
    QVBoxLayout,
    QWidget,
    QListWidget,
    QPushButton,
    QLabel,
)
from PyQt5.QtGui import QPixmap, QIcon
from PyQt5.QtCore import Qt, QFile, QSize
from SerumWriter.Globals import palette

class Selection:
    def __init__(self, title, icon: str=None):
        self.title: str = title
        self.icon: str = icon
        
class SuggestButton(QPushButton):
    def __init__(self, selection: 'Selection', parent=None):
        super().__init__(parent=parent)
        self.selection = selection

        self.setText(self.selection.title)
        if self.selection.icon:
            import from SerumWriter.Themes.Dark.style_rc
            
            self.setIcon(QIcon(self.selection.icon))
            self.setIconSize(QSize(32, 32))
        


class LineEdit(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(10, 25, 10, 25)
        self.setLayout(self._layout)


        self.setWindowFlag(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)

        shadow = QGraphicsDropShadowEffect(self)
        shadow.setBlurRadius(50)
        shadow.setOffset(0, 5)
        

        self.lineEdit = QLineEdit()
        self.lineEdit.setPlaceholderText('Start typing..')
        self.lineEdit.setTextMargins(15, 15, 15, 15)        
        self.lineEdit.setObjectName('LineEdit')    

        # self.row = [QWidget() for i in range(5)]
        # self.list = QListWidget()
        # self.list.setGraphicsEffect(shadow)
        # # self.list.setMaximumHeight(60)
        # self.list.setObjectName('ListWidget')

        self.setStyleSheet(
            '''
            QLineEdit#LineEdit {{
                border-radius: 5px;
                background-color: {bg};
                height: 50px;
                font-size: 15px;
                font-family: 'Segoe UI';
            }}
            SuggestButton {{
                text-align: left;
                padding-left: 25px;
                
                background-color: {bg};
                height: 50px;
                font-size: 15px;
                font-family: 'Segoe UI';
                border-radius: 5px;
            }}
            SuggestButton:hover {{
                background-color: #1a1a1a;
            }}
            '''.format(
                bg='#181818'
            )
        )
        btn = SuggestButton(
            Selection('Header', icon=r"C:\Users\vince\Downloads\icons8-h-48.png")
        )
        self.setMinimumHeight(10)
        self.setGraphicsEffect(shadow)
        self._layout.addWidget(self.lineEdit, alignment=Qt.AlignmentFlag.AlignTop)
        self._layout.addWidget(btn)
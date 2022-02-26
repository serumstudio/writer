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

#: From https://github.com/zhiyiYo/PyQt-Fluent-Widgets/tree/master/widgets/message_dialog

import textwrap

from PyQt5.QtCore import (
    Qt, 
    pyqtSignal, 
    QPropertyAnimation, 
    QEasingCurve, 
)

from PyQt5.QtWidgets import (
    QDialog, QGraphicsDropShadowEffect,
    QGraphicsOpacityEffect, QLabel, 
    QPushButton, QWidget, QVBoxLayout,
    QHBoxLayout, QLabel, QPushButton
)
from SerumWriter.Components.Window import FramelessWindow


class Sidebar(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setFixedWidth(250)
        
        self._layout = QVBoxLayout()
        self._layout.setContentsMargins(0,0,0,0)
        self.setLayout(self._layout)
        self.setStyleSheet('background-color: #181818;')
        self.label = QLabel()
        self.label.setText('')

        # self.label.setAlignment(Qt.AlignmentFlag.AlignHCenter)
        self._layout.addWidget(self.label)


class Preference(FramelessWindow):
    def __init__(self, parent=None):
        super().__init__(parent=parent)
        titlebar = self.titlebar()
        titlebar.setStyleSheet('background-color: transparent;')
        titlebar.buttonsWidget.btnMaximize.setVisible(False)
        titlebar.buttonsWidget.btnMinimize.setVisible(False)
        titlebar.buttonsWidget.btnRestore.setVisible(False)
        
        self.hboxlayout = QHBoxLayout()
        self.addContentLayout(self.hboxlayout)

        sidebar = Sidebar(self)
        widget = QWidget()
        
        self.hboxlayout.addWidget(sidebar)
        self.hboxlayout.addWidget(widget)

class MaskDialog(QDialog):

    yesSignal = pyqtSignal()
    cancelSignal = pyqtSignal()

    def __init__(self, title: str, content: str, parent):
        super().__init__(parent=parent)
        self.content = content
        self.windowMask = QWidget(self)
        self.windowMask.setWindowOpacity(0)
        self.widget = QWidget(self)
        self.titleLabel = QLabel(title, self.widget)
        self.contentLabel = QLabel(content, self.widget)
        self.yesButton = QPushButton('Yes', self.widget)
        self.cancelButton = QPushButton('Cancel', self.widget)
        self.init_widget()

    def init_widget(self, parent_width: int=None, parent_height: int=None):
        if not parent_width:
            parent_width = self.parent().width()
        if not parent_height:
            parent_height = self.parent().height()
        
        self.__setShadowEffect()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setGeometry(0, 0, parent_width, parent_height)
        self.windowMask.resize(self.size())
        self.widget.setMaximumWidth(675)
        self.titleLabel.move(30, 30)
        self.contentLabel.move(30, 70)
        
        self.contentLabel.setText("\n".join(
                textwrap.wrap(
                    self.content, 50, replace_whitespace=False
                )
            )
        )
        self.__setQss()
        self.init_layout()

        self.yesButton.clicked.connect(self.__onYesButtonClicked)
        self.cancelButton.clicked.connect(self.__onCancelButtonClicked)

    def __setShadowEffect(self):

        shadowEffect = QGraphicsDropShadowEffect(self.widget)
        shadowEffect.setBlurRadius(50)
        shadowEffect.setOffset(0, 5)
        self.widget.setGraphicsEffect(shadowEffect)

    def showEvent(self, e):
        self.__setShadowEffect()
        opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacityEffect)
        opacityAni = QPropertyAnimation(opacityEffect, b'opacity', self)
        opacityAni.setStartValue(0)
        opacityAni.setEndValue(1)
        opacityAni.setDuration(200)
        opacityAni.setEasingCurve(QEasingCurve.InSine)
        opacityAni.finished.connect(opacityEffect.deleteLater)
        opacityAni.start()
        super().showEvent(e)

    def closeEvent(self, e):

        self.widget.setGraphicsEffect(None)
        opacityEffect = QGraphicsOpacityEffect(self)
        self.setGraphicsEffect(opacityEffect)
        opacityAni = QPropertyAnimation(opacityEffect, b'opacity', self)
        opacityAni.setStartValue(1)
        opacityAni.setEndValue(0)
        opacityAni.setDuration(100)
        opacityAni.setEasingCurve(QEasingCurve.OutCubic)
        opacityAni.finished.connect(self.hide)
        opacityAni.start()
        e.ignore()

    def init_layout(self):

        self.contentLabel.adjustSize()
        self.widget.setFixedSize(60+self.contentLabel.width(),
                                 self.contentLabel.y() + self.contentLabel.height()+115)
        self.widget.move(self.width()//2 - self.widget.width()//2,
                         self.height()//2 - self.widget.height()//2)
        self.yesButton.resize((self.widget.width() - 68) // 2, 40)
        self.cancelButton.resize(self.yesButton.width(), 40)
        self.yesButton.move(30, self.widget.height()-70)
        self.cancelButton.move(
            self.widget.width()-30-self.cancelButton.width(), self.widget.height()-70)


    def __onCancelButtonClicked(self):
        self.cancelSignal.emit()
        self.close()

    def __onYesButtonClicked(self):
        self.yesSignal.emit()
        self.close()

    def __setQss(self):
        self.widget.setObjectName('DialogWidget')
        self.windowMask.setObjectName('windowMask')
        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')
        
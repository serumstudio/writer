

from PyQt5.QtWidgets import (
    QWidget,
    QHBoxLayout,
    QLabel
)

class Statusbar(QWidget):
    def __init__(self, parent=None):
        super(Statusbar, self).__init__(parent=parent)
        self._layout = QHBoxLayout()
        self.setMinimumWidth(parent.width() / 4)
        self.setLayout(self._layout)
        # self.setStyleSheet('background-color: red;')

    def addLabel(self, s: str, objectName: str=None):
        l = QLabel()
        l.setText(s)
        if objectName:
            l.setObjectName(objectName)

        #: Always set the index to 0
        
        self._layout.insertWidget(0, l) 

        return l

    def addWidget(self, w: QWidget):
        self._layout.insertWidget(0, w)
        return w
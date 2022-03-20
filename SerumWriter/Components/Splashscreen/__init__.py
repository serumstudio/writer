
from PyQt5.QtWidgets import (
    QWidget,
    QDesktopWidget,
    QHBoxLayout,
    QLabel
)
from PyQt5.QtGui import (
    QPixmap,
    QIcon
)
from PyQt5.QtCore import (
    Qt,
    QPoint
)
from SerumWriter.Components.Splashscreen import res


class SplashScreen(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowIcon(QIcon(':/image/logo.png'))
        self.setWindowTitle('Serum Writer')
        splash_pixmap = QPixmap(':/image/splashscreen.png')
        pixmap = QLabel()
        pixmap.setPixmap(splash_pixmap)
        layout = QHBoxLayout()
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.FramelessWindowHint)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        self.setLayout(layout)
        layout.addWidget(pixmap)
        self.show()

        fm = self.frameGeometry()
        cp = QDesktopWidget().availableGeometry().center()
        fm.moveCenter(cp)
        self.move(fm.topLeft())
        self.oldPos = self.pos()

    def mousePressEvent(self, event):
        self.oldPos = event.globalPos()

    def mouseMoveEvent(self, event):
        delta = QPoint (event.globalPos() - self.oldPos)
        self.move(self.x() + delta.x(), self.y() + delta.y())
        self.oldPos = event.globalPos()
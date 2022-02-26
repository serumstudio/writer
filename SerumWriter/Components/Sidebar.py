

from PyQt5.QtWidgets import (
    QWidget
)
from PyQt5.QtCore import (
    QPoint,
    QPropertyAnimation,
    QEasingCurve
)

class Sidebar(QWidget):
    def __init__(
        self, 
        parent=None
    ):
        super(Sidebar, self).__init__(parent)
        self.setMinimumWidth(45)
        
        self.setStyleSheet('background-color: red;')
        self.animIn = QPropertyAnimation(self, b'geometry', duration=500, easingCurve=QEasingCurve.OutCubic)
        self.animIn.setPropertyName(b'pos')
        self.animOut = QPropertyAnimation(self, b'geometry', duration=500, easingCurve=QEasingCurve.Type.OutCubic)
        self.animOut.setPropertyName(b'pos')
        
        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)

    def animation(self):
        if self.isHidden():
        
            self.hide()
            self.setGeometry(
                0,
                0,
                int(self.geometry().width()),
                int(self.geometry().height())        
            )
            
            self.animIn.setStartValue(QPoint(-self.width(), 0))
            self.animIn.setEndValue(QPoint(0,0))
        
            self.animIn.start()
            self.show()

        elif not self.isHidden():
            self.animIn.stop()
            geometry = self.geometry()
            self.animOut.setStartValue(geometry.topLeft())
            self.animOut.setEndValue(QPoint(-self.width(), 0))
            self.animOut.start()
            self.animOut.finished.connect(self.hide)



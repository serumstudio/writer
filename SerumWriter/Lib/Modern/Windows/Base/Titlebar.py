from PyQt5.QtWidgets import (
    QFrame, 
    QMenu, 
    QHBoxLayout, 
)

from PyQt5.QtCore import (
    pyqtSignal as Signal, 
    QPoint, 
    QMetaObject, 
    pyqtSlot as Slot, 
    Qt, 
    QRect,
    QPropertyAnimation,
    QEasingCurve
)
from PyQt5.QtGui import QPalette, QIcon
from .Buttons import (
    ButtonsWidget, 
    AppLogo, 
    MenuButton, 
    SettingsButton 
)

import SerumWriter.Lib.Modern as Modern
from SerumWriter.Globals import palette


class Titlebar(QFrame):
    """Titlebar for frameless windows."""

    minimizeClicked = Signal()
    maximizeClicked = Signal()
    restoreClicked = Signal()
    closeClicked = Signal()
    settings_clicked = Signal()
    show_event = Signal()
    def __init__(self, parent=None):
        super(Titlebar, self).__init__(parent=parent)
        self.setObjectName("titlebar")
        self.setMouseTracking(True)

        self.menus = []

        self.setAutoFillBackground(True)
        self.setFixedHeight(30)
        self.setContentsMargins(0, 0, 0, 0)
        self.setBackgroundRole(QPalette.Highlight)
        
        #: My text edior is not determining the layout as QHBoxLayout.
        self.layout: 'QHBoxLayout' = QHBoxLayout(self)
        self.layout.setAlignment(Qt.AlignVCenter)
        self.layout.setAlignment(Qt.AlignLeft)
        self.layout.setContentsMargins(8, 0, 0, 0)
        self.layout.setSpacing(0)
        self.setLayout(self.layout)


        # Animations
        self.animIn = QPropertyAnimation(self, b'geometry', duration=500, easingCurve=QEasingCurve.OutCubic)
        self.animIn.setPropertyName(b'pos')
        self.animOut = QPropertyAnimation(self, b'geometry', duration=500, easingCurve=QEasingCurve.Type.OutCubic)
        self.animOut.setPropertyName(b'pos')
        

        self.appLogoLabel = AppLogo(self)
        
        #: For now, we will replace the app logo to menu button

        # if Modern.APP_ICON_PATH:
        #     self.appLogoLabel.setPixmap(QPixmap(Modern.APP_ICON_PATH))
        #     self.layout.setContentsMargins(2, 0, 0, 0)
        # self.layout.addWidget(self.appLogoLabel)
        # if Modern.ALIGN_BUTTONS_LEFT:
        #     self.appLogoLabel.setVisible(False)
        #     self.layout.setContentsMargins(8, 0, 0, 0)

        self.settings_btn = SettingsButton(self)
        self.settings_btn.clicked.connect(self.settings_clicked.emit)
        self.layout.addWidget(self.settings_btn)
        self.layout.setContentsMargins(0,0,0,0)

        self.settings_btn.hide()


        self.layout.insertStretch(50)
        self.buttonsWidget = ButtonsWidget(self)
        if Modern.ALIGN_BUTTONS_LEFT:
            self.layout.insertWidget(0, self.buttonsWidget)
        else:
            self.layout.addWidget(self.buttonsWidget)

        # auto connect signals
        QMetaObject.connectSlotsByName(self)
        if self.window().parent() is not None:
            self.buttonsWidget.btnRestore.setVisible(False)
            self.buttonsWidget.btnMaximize.setVisible(False)
            self.buttonsWidget.btnMinimize.setVisible(False)

        policy = self.sizePolicy()
        policy.setRetainSizeWhenHidden(True)
        self.setSizePolicy(policy)

    def bottomBorderColor(self, show: bool=True):
        if show:
            self.setStyleSheet('border-bottom: 0.5px solid {};'.format(palette.TITLEBAR_BOTTOM_BORDER))
        else:
            self.setStyleSheet('border-bottom: none;')
            
    def showSettingsButton(self):
        self.settings_btn.show()


    def setWindowIcon(self, icon: QIcon):
        self.appLogoLabel.setPixmap(icon.pixmap())

    def animation(self, animIn=False, animOut=False):
        
        if animIn and self.isHidden():
        
            self.hide()
            self.setGeometry(
                0,
                0,
                int(self.geometry().width()),
                int(self.geometry().height())        
            )
            
            self.animIn.setStartValue(QPoint(0, -self.height()))
            self.animIn.setEndValue(QPoint(0,0))
            self.show_event.emit()
            self.animIn.start()
            self.show()
        elif animOut and not self.isHidden():
            self.animIn.stop()
            geometry = self.geometry()
            self.animOut.setStartValue(QPoint(0, geometry.y()))
            self.animOut.setEndValue(QPoint(0, -self.height()))
            self.animOut.start()
            self.animOut.finished.connect(self.hide)

        
    # connecting buttons signals
    @Slot()
    def on_btnClose_clicked(self):
        self.closeClicked.emit()

    @Slot()
    def on_btnRestore_clicked(self):
        self.showRestoreButton(False)
        self.showMaximizeButton(True)
        self.window().showNormal()
        self.restoreClicked.emit()

    @Slot()
    def on_btnMaximize_clicked(self):
        if Modern.USE_DARWIN_BUTTONS:
            if self.window().isMaximized():
                self.window().showNormal()
            else:
                self.window().showMaximized()
        else:
            self.showRestoreButton(True)
            self.showMaximizeButton(False)
            self.window().showMaximized()
        self.maximizeClicked.emit()

    @Slot()
    def on_btnMinimize_clicked(self):
        self.window().showMinimized()

    def showLogo(self, value: bool):
        """Show or hide app logo label"""
        self.appLogoLabel.setVisible(value)

    def showRestoreButton(self, value):
        if self.window().parent() is None:
            self.buttonsWidget.btnRestore.setVisible(value)

    def showMaximizeButton(self, value):
        if self.window().parent() is None:
            self.buttonsWidget.btnMaximize.setVisible(value)

    def showMinimizeButton(self, value):
        if self.window().parent() is None:
            self.buttonsWidget.btnMinimize.setVisible(value)


    def addMenu(self, menu: QMenu):
        menuButton = MenuButton(self)
        menuButton.setMenu(menu)
        menuButton.setText(menu.title())
        self.layout.insertWidget(len(self.menus) + 1, menuButton)
        self.menus.append(menuButton)

    def setTitlebarHeight(self, height: int):
        self.setFixedHeight(height)

    

    def mouseOverTitlebar(self, x, y):
        self.animation(animIn=True)

        
        if self.childAt(QPoint(x, y)):
            return False
        else:
            return QRect(self.appLogoLabel.width(), 0,
                         self.width() - self.appLogoLabel.width(),
                         self.height()).contains(QPoint(x, y))
     
        
        
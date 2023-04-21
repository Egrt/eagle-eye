import sys
from PyQt5.QtCore import Qt, QRect, QLocale, QTranslator
from PyQt5.QtGui import QIcon, QPainter, QImage, QBrush, QColor, QFont
from PyQt5.QtWidgets import QApplication, QFrame, QStackedWidget, QHBoxLayout, QLabel

from qfluentwidgets import (NavigationInterface,NavigationItemPosition, NavigationWidget, MessageBox,
                            isDarkTheme, setTheme, Theme)
from qfluentwidgets import FluentIcon as FIF
from qframelesswindow import FramelessWindow, TitleBar
from configs.setting_interface import SettingInterface
from YoloSort.video_interface import VideoInterface
from configs.config import cfg, Language


class Widget(QFrame):

    def __init__(self, text: str, parent=None):
        super().__init__(parent=parent)
        self.setObjectName(text.replace(' ', '-'))
        self.label = QLabel(text, self)
        self.label.setAlignment(Qt.AlignCenter)
        self.hBoxLayout = QHBoxLayout(self)
        self.hBoxLayout.addWidget(self.label, 1, Qt.AlignCenter)

        # leave some space for title bar
        self.hBoxLayout.setContentsMargins(0, 32, 0, 0)


class AvatarWidget(NavigationWidget):
    """ Avatar widget """

    def __init__(self, parent=None):
        super().__init__(isSelectable=False, parent=parent)
        self.avatar = QImage('resource/logo.png').scaled(
            24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.SmoothPixmapTransform | QPainter.Antialiasing)

        painter.setPen(Qt.NoPen)

        if self.isPressed:
            painter.setOpacity(0.7)

        # draw background
        if self.isEnter:
            c = 255 if isDarkTheme() else 0
            painter.setBrush(QColor(c, c, c, 10))
            painter.drawRoundedRect(self.rect(), 5, 5)

        # draw avatar
        painter.setBrush(QBrush(self.avatar))
        painter.translate(8, 6)
        painter.drawEllipse(0, 0, 24, 24)
        painter.translate(-8, -6)

        if not self.isCompacted:
            painter.setPen(Qt.white if isDarkTheme() else Qt.black)
            font = QFont('Segoe UI')
            font.setPixelSize(14)
            painter.setFont(font)
            painter.drawText(QRect(44, 0, 255, 36), Qt.AlignVCenter, '白鹭先生')


class CustomTitleBar(TitleBar):
    """ Title bar with icon and title """

    def __init__(self, parent):
        super().__init__(parent)
        # add window icon
        self.iconLabel = QLabel(self)
        self.iconLabel.setFixedSize(18, 18)
        self.hBoxLayout.insertSpacing(0, 10)
        self.hBoxLayout.insertWidget(1, self.iconLabel, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.window().windowIconChanged.connect(self.setIcon)

        # add title label
        self.titleLabel = QLabel(self)
        self.hBoxLayout.insertWidget(2, self.titleLabel, 0, Qt.AlignLeft | Qt.AlignBottom)
        self.titleLabel.setObjectName('titleLabel')
        self.window().windowTitleChanged.connect(self.setTitle)

    def setTitle(self, title):
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setIcon(self, icon):
        self.iconLabel.setPixmap(QIcon(icon).pixmap(18, 18))


class Window(FramelessWindow):

    def __init__(self):
        super().__init__()
        self.setTitleBar(CustomTitleBar(self))
        # 设置主题色
        self.setQss()

        self.hBoxLayout = QHBoxLayout(self)
        self.navigationInterface = NavigationInterface(
            self, showMenuButton=True, showReturnButton=True)
        self.stackWidget = QStackedWidget(self)

        # 设置子界面
        self.videoInterface   = VideoInterface(self)
        self.folderInterface  = Widget('入侵报警', self)
        self.settingInterface = SettingInterface(self)

        self.stackWidget.addWidget(self.videoInterface)
        self.stackWidget.addWidget(self.folderInterface)
        self.stackWidget.addWidget(self.settingInterface)

        # 初始化layout
        self.initLayout()

        # 添加跳转界面
        self.initNavigation()

        self.initWindow()

    def initLayout(self):
        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.addWidget(self.navigationInterface)
        self.hBoxLayout.addWidget(self.stackWidget)
        self.hBoxLayout.setStretchFactor(self.stackWidget, 1)

        self.titleBar.raise_()
        self.navigationInterface.displayModeChanged.connect(self.titleBar.raise_)

    def setQss(self):
        theme = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/qss/{theme}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def initNavigation(self):
        self.navigationInterface.addItem(
            routeKey='实时监测',
            icon=FIF.VIDEO,
            text='实时监测',
            onClick=lambda: self.switchTo(self.videoInterface)
        )

        self.navigationInterface.addSeparator()

        # add navigation items to scroll area
        self.navigationInterface.addItem(
            routeKey=self.folderInterface.objectName(),
            icon=FIF.FOLDER,
            text='入侵报警',
            onClick=lambda: self.switchTo(self.folderInterface),
            position=NavigationItemPosition.SCROLL
        )

        # add custom widget to bottom
        self.navigationInterface.addWidget(
            routeKey='头像',
            widget=AvatarWidget(),
            onClick=self.showMessageBox,
            position=NavigationItemPosition.BOTTOM
        )

        self.navigationInterface.addItem(
            routeKey=self.settingInterface.objectName(),
            icon=FIF.SETTING,
            text='设置',
            onClick=lambda: self.switchTo(self.settingInterface),
            position=NavigationItemPosition.BOTTOM
        )

        self.stackWidget.currentChanged.connect(self.onCurrentInterfaceChanged)
        self.stackWidget.setCurrentIndex(0)

    def initWindow(self):
        self.resize(900, 700)
        self.setWindowIcon(QIcon('resource/logo.png'))
        self.setWindowTitle('鹰眼系统')
        self.titleBar.setAttribute(Qt.WA_StyledBackground)

        desktop = QApplication.desktop().availableGeometry()
        w, h = desktop.width(), desktop.height()
        self.move(w//2 - self.width()//2, h//2 - self.height()//2)

        self.setQss()

    def setQss(self):
        color = 'dark' if isDarkTheme() else 'light'
        with open(f'resource/{color}/demo.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def switchTo(self, widget):
        self.stackWidget.setCurrentWidget(widget)

    def onCurrentInterfaceChanged(self, index):
        widget = self.stackWidget.widget(index)
        self.navigationInterface.setCurrentItem(widget.objectName())

    def showMessageBox(self):
        w = MessageBox(
            '关于',
            'BY: 白鹭先生 西南科技大学智能控制与图像处理研究室',
            self
        )
        w.exec()

    def resizeEvent(self, e):
        self.titleBar.move(46, 0)
        self.titleBar.resize(self.width()-46, self.titleBar.height())
    
    def closeEvent(self, event):
        if cfg.minimizeToTray.value:
            self.showMinimized()
            event.ignore()
        else:
            event.accept()


if __name__ == '__main__':

    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.AA_EnableHighDpiScaling)
    QApplication.setAttribute(Qt.AA_UseHighDpiPixmaps)

    app = QApplication(sys.argv)

    # internationalization
    translator = QTranslator()
    language = cfg.get(cfg.language)

    if language == Language.AUTO:
        translator.load(QLocale.system(), "resource/i18n/qfluentwidgets_")
    elif language != Language.ENGLISH:
        translator.load(f"resource/i18n/qfluentwidgets_{language.value}.qm")
    app.installTranslator(translator)
    w = Window()
    w.show()
    app.exec_()
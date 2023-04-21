from configs.config import cfg, HELP_URL, FEEDBACK_URL, AUTHOR, VERSION, YEAR
from qfluentwidgets import (PushButton, PrimaryPushButton, HyperlinkButton,
                            setTheme, Theme, ToolButton, ScrollArea, InfoBar,
                            InfoBarIcon, InfoBarPosition)
from qfluentwidgets import FluentIcon as FIF
from PyQt5.QtCore import Qt, pyqtSignal, QUrl, QStandardPaths, QThread, QSize
from PyQt5.QtGui import QPainter, QPixmap, QImage, QColor
from PyQt5.QtWidgets import (QWidget, QLabel, QFontDialog, QFileDialog, QTableWidget,
                             QHBoxLayout, QVBoxLayout, QSplitter, QScrollArea, QFrame, 
                             QListWidgetItem, QListWidget, QDialog, QGraphicsDropShadowEffect)
from YoloSort.AIDetector import Detector
import cv2
import time
import numpy as np
        
class VideoInterface(ScrollArea):
    """ Setting interface """
    polygon_complete = pyqtSignal(list)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        # 加载目标监测追踪模型
        self.detector     = Detector()
        self.showInfoBar('成功加载模型')
        # 设置主窗口的中心部件
        self.central_widget = QWidget(self)
        self.imageLabel   = QLabel(self)
        self.detactStatus = False
        self.drawingPolygon = False
        self.points       = []
        self.__initWidget()

    def __initWidget(self):
        self.resize(1000, 800)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setViewportMargins(0, 50, 0, 20)
        self.setWidget(self.central_widget)
        self.setWidgetResizable(True)

        # initialize style sheet
        self.__setQss(cfg.theme)

        # initialize layout
        self.__initLayout()
        self.__connectSignalToSlot()

    def __initLayout(self):
        
        # 创建左侧控件
        left_widget = QWidget(self)
        left_layout = QVBoxLayout(left_widget)

        # 创建上部分控件，用来放置按钮
        top_widget = QWidget(left_widget)
        top_layout = QHBoxLayout(top_widget)
        self.buttonLoadVideo   = PushButton('打开视频', self)
        self.buttonDrawPolygon = PushButton('绘制禁行区域', self)
        top_layout.addWidget(self.buttonLoadVideo)
        top_layout.addWidget(self.buttonDrawPolygon)
        left_layout.addWidget(top_widget)

        # 创建下部分控件
        self.bottom_widget = QListWidget(left_widget)
        self.bottom_layout = QVBoxLayout(self.bottom_widget)
        left_layout.addWidget(self.bottom_widget)
        

        # 创建右侧控件
        right_widget = QWidget(self)
        right_layout = QVBoxLayout(right_widget)
        # 图片添加阴影
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setXOffset(0)
        shadow.setYOffset(0)
        shadow.setColor(QColor(0, 0, 0, 100))
        self.imageLabel.setGraphicsEffect(shadow)
        right_layout.addWidget(self.imageLabel)

        # 创建分割器
        splitter = QSplitter(self)
        splitter.addWidget(left_widget)
        splitter.addWidget(right_widget)
        splitter.setSizes([self.width()//3, self.width()*2//3])

        # 创建主布局
        main_layout = QHBoxLayout()
        main_layout.addWidget(splitter)

        self.central_widget.setLayout(main_layout)

    def __setQss(self, theme: Theme):
        """ set style sheet """

        theme = 'dark' if theme == Theme.DARK else 'light'
        with open(f'resource/qss/{theme}/setting_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __showRestartTooltip(self):
        """ show restart tooltip """
        InfoBar.warning(
            '',
            self.tr('Configuration takes effect after restart'),
            parent=self.window()
        )

    def __onThemeChanged(self, theme: Theme):
        """ theme changed slot """
        # change the theme of qfluentwidgets
        setTheme(theme)

        # chang the theme of setting interface
        self.__setQss(theme)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        cfg.appRestartSig.connect(self.__showRestartTooltip)
        cfg.themeChanged.connect(self.__onThemeChanged)
        # 文件选择槽函数绑定
        self.buttonLoadVideo.clicked.connect(self.getVideoPath)  
        self.buttonDrawPolygon.clicked.connect(self.start_drawingPolygon)
    
    def getVideoPath(self):
        if not self.detactStatus:
            file_path, _ = QFileDialog.getOpenFileName()
            if file_path:
                self.showInfoBar('开始处理视频文件：{}'.format(file_path))
                # 创建视频线程
                self.videoThread = VideoThread(file_path, self.detector)
                self.videoThread.change_pixmap_signal.connect(self.updateFrame)
                self.videoThread.add_illegal_person.connect(self.updateInfoItem)
                self.videoThread.start()
                self.detactStatus = True
                self.buttonLoadVideo.setText("终止处理")
            else:
                self.showWarnBar('请选择视频文件')
        else:
            self.videoThread.stop()
            self.detactStatus = False
            image = QImage(1080, 720, QImage.Format_RGB888)
            image.fill(Qt.white)
            self.updateFrame(image)
            self.buttonLoadVideo.setText("打开视频")

    def updateFrame(self, image):
        # 将QImage转换为QPixmap格式，并显示在QLabel上
        pixmap = QPixmap.fromImage(image)
        self.imageLabel.setPixmap(pixmap)

    def updateInfoItem(self, tracker):
        # 总Widget
        wight = QWidget()
        # 总体横向布局
        layout_main = QHBoxLayout()
        # 右边的纵向布局
        layout_right = QVBoxLayout()
        # 右下的的横向布局
        layout_right_down = QHBoxLayout()  # 右下的横向布局
        layout_right_down.addWidget(QLabel(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))

        # 按照从左到右, 从上到下布局添加
        object_image = cv2.cvtColor(tracker.object_image, cv2.COLOR_RGB2BGR)
        object_image = cv2.resize(object_image, (200, 600), 3)
        # Add the pedestrian image to the layout
        qimage = QImage(object_image, object_image.shape[1], object_image.shape[0], QImage.Format_RGB888)
        pedestrian_pixmap = QPixmap.fromImage(qimage)
        pedestrian_pixmap = pedestrian_pixmap.scaled(100, 300, Qt.KeepAspectRatio)
        pedestrian_label = QLabel(self)
        pedestrian_label.setPixmap(pedestrian_pixmap)
        layout_main.addWidget(pedestrian_label)  # 最左边的图片
        layout_right.addWidget(QLabel('违规闯入！请及时处理！'))  # 右边的纵向布局
        layout_right.addLayout(layout_right_down)  # 右下角横向布局
        layout_main.addLayout(layout_right)  # 右边的布局
        wight.setLayout(layout_main)  # 布局给wight
        item = QListWidgetItem()  # 创建QListWidgetItem对象
        item.setSizeHint(QSize(300, 200))  # 设置QListWidgetItem大小
        
        # 添加按钮
        button = PushButton('查看详情', self)
        button.clicked.connect(lambda: self.showDetail(pedestrian_pixmap, '违规闯入！请及时处理！', time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())))
        layout_main.addWidget(button)

        self.bottom_widget.addItem(item)  # 添加item
        self.bottom_widget.setItemWidget(item, wight)  # 为item设置widget
        self.showWarnBar('违规闯入！请及时处理！')

    def showDetail(self, pixmap, info, time):
        """ show detail """
        # 总Widget
        wight = QWidget()
        # 总体横向布局
        layout_main = QHBoxLayout()
        # 右边的纵向布局
        layout_right = QVBoxLayout()
        # 右下的的横向布局
        layout_right_down = QHBoxLayout()  # 右下的横向布局
        layout_right_down.addWidget(QLabel(time))

        # Add the pedestrian image to the layout
        pedestrian_label = QLabel(self)
        pedestrian_label.setPixmap(pixmap)
        layout_main.addWidget(pedestrian_label)  # 最左边的图片
        layout_right.addWidget(QLabel(info))  # 右边的纵向布局
        layout_right.addLayout(layout_right_down)  # 右下角横向布局
        layout_main.addLayout(layout_right)  # 右边的布局
        wight.setLayout(layout_main)  # 布局给wight
        
        # 显示窗口
        dialog = QDialog(self)
        dialog.setWindowTitle('详情')
        dialog.resize(400, 600)
        dialog.setLayout(QVBoxLayout())
        dialog.layout().addWidget(wight)
        dialog.exec_()

    def showInfoBar(self, content):
        InfoBar.success(
            title='提示',
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )
    def showWarnBar(self, content):
        InfoBar.warning(
            title='警告',
            content=content,
            orient=Qt.Horizontal,
            isClosable=True,
            position=InfoBarPosition.TOP,
            duration=1000,
            parent=self
        )

    def start_drawingPolygon(self):
        if not self.drawingPolygon and self.detactStatus:
            self.buttonDrawPolygon.setText('结束绘制')
            self.drawingPolygon = True
            self.points = []
            self.imageLabel.mousePressEvent = self.add_point_to_polygon
            self.imageLabel.mouseDoubleClickEvent = self.finish_drawingPolygon
        else:
            self.drawingPolygon = False
            self.buttonDrawPolygon.setText('绘制禁行区域')


    def add_point_to_polygon(self, event):
        if self.drawingPolygon:
            x = event.pos().x()
            y = event.pos().y()
            self.points.append([x, y])
            print(self.points)
            self.videoThread.points = self.points
    
    def finish_drawingPolygon(self, event):
        if self.drawingPolygon:
            self.drawingPolygon = False
            self.buttonDrawPolygon.setText('绘制禁行区域')
            
        

class VideoThread(QThread):
    change_pixmap_signal = pyqtSignal(QImage)
    add_illegal_person = pyqtSignal(object)

    def __init__(self, file_path, detector):
        super().__init__()
        self.file_path = file_path
        self.stop_flag = False
        self.detector  = detector
        self.points    = []
        self.image_shape = [1080, 720]
        self.illegal_person = {}
        

    def run(self):
        cap = cv2.VideoCapture(self.file_path)
        while not self.stop_flag:
            ret, frame = cap.read()
            if ret:
                result = self.detector.feedCap(frame)
                image  = result['frame']
                object_bboxes = result['object_bboxes']
                points = np.array(self.points)
                object_bboxes_new = []
                for object in object_bboxes:
                    x1, y1, x2, y2, cls_name, track_id = object
                    object_new = [x1, y1, x2, y2, cls_name, track_id, False]
                    object_bboxes_new.append(object_new)
                if len(points) > 0:
                    scale_w = image.shape[1] / self.image_shape[0]
                    scale_h = image.shape[0] / self.image_shape[1]
                    points[:, 0] = points[:, 0]*scale_w
                    points[:, 1] = points[:, 1]*scale_h
                    # 判断行人是否进入禁区
                    for idx, object in enumerate(object_bboxes_new):
                        x1, y1, x2, y2, cls_name, track_id, _  = object
                        if cv2.pointPolygonTest(points, ((x1+x2)/2, (y1+y2)/2), False) >= 0:
                            object_bboxes_new[idx][6] = True
                            if track_id not in self.illegal_person:
                                self.illegal_person[track_id] = Tracker(object, image)
                                self.add_illegal_person.emit(Tracker(object, image))
                            else:
                                pass
                        else:
                            pass
                    image = cv2.polylines(image, [points], True, (0, 255, 0), thickness=2)
                self.draw_boxes(image, object_bboxes_new)
                image = cv2.resize(image, tuple(self.image_shape), 3)
                image = QImage(image, self.image_shape[0], self.image_shape[1], QImage.Format_RGB888).rgbSwapped()
                self.change_pixmap_signal.emit(image)
            else:
                break
        cap.release()

    def update_file_path(self, file_path):
        self.file_path = file_path

    def stop(self):
        self.stop_flag = True

    def draw_boxes(self, img, bboxes):
        for bbox in bboxes:
            x1, y1, x2, y2, cls_name, track_id, illegal = bbox
            x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
            color = (255, 0, 0) if illegal else (255, 255, 255) 
            label = '{}{:d}'.format(cls_name, track_id)
            cv2.rectangle(img,(x1, y1),(x2,y2),color,2)
            cv2.putText(img,label,(x1,y1), cv2.FONT_HERSHEY_PLAIN, 1, color, 2)
        return img
    
class Tracker(object):

    def __init__(self, object, image):
        x1, y1, x2, y2, cls_name, track_id, _ = object
        bbox = np.array([x1, y1, x2, y2], dtype=np.int32)
        self.cls_name = cls_name
        self.track_id = track_id
        self.bbox = bbox
        self.object_image = image[int(y1):int(y2), int(x1):int(x2)]

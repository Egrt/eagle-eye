'''
Author: Egrt
Date: 2021-12-06 12:40:15
LastEditors: Egrt
LastEditTime: 2023-03-13 16:15:32
FilePath: \yolox-deepsortd:\notebook\yolox-deepsort\YoloDeepSort\BaseDetector.py
'''
from YoloSort.Tracker import update_tracker
import cv2


class BaseDet(object):

    def __init__(self):

        self.stride = 1

    def build_config(self):

        self.faceTracker = {}
        self.faceClasses = {}
        self.faceLocation1 = {}
        self.faceLocation2 = {}
        self.frameCounter = 0
        self.currentCarID = 0
        self.recorded = []

        self.font = cv2.FONT_HERSHEY_SIMPLEX

    def feedCap(self, im):

        retDict = {
            'frame': None,
            'list_of_ids': None,
            'object_bboxes': []
        }
        self.frameCounter += 1

        im, object_bboxes = update_tracker(self, im)
    
        retDict['frame'] = im
        retDict['object_bboxes'] = object_bboxes

        return retDict

    def init_model(self):
        raise EOFError("Undefined model type.")

    def preprocess(self):
        raise EOFError("Undefined model type.")

    def detect(self):
        raise EOFError("Undefined model type.")

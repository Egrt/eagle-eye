'''
Author: Egrt
Date: 2021-12-06 12:40:16
LastEditors: Egrt
LastEditTime: 2023-04-20 14:29:08
FilePath: \yolox-deepsort\YoloDeepSort\tracker.py
'''
from .ocsort.ocsort import OCSort
import numpy as np
import cv2

palette = (2 ** 11 - 1, 2 ** 15 - 1, 2 ** 20 - 1)

ocsort = OCSort()
def compute_color_for_labels(label):
    """
    Simple function that adds fixed color depending on the class
    """
    color = [int((p * (label ** 2 - label + 1)) % 255) for p in palette]
    return tuple(color)


def draw_boxes(img, bbox, offset=(0,0)):
    for x1, y1, x2, y2, cls_name, track_id in bbox:
        x1, y1, x2, y2 = int(x1), int(y1), int(x2), int(y2)
        x1 += offset[0]
        x2 += offset[0]
        y1 += offset[1]
        y2 += offset[1]
        color = compute_color_for_labels(track_id)
        label = '{}{:d}'.format(cls_name, track_id)
        cv2.rectangle(img,(x1, y1),(x2,y2),color,2)
        cv2.putText(img,label,(x1,y1), cv2.FONT_HERSHEY_PLAIN, 1, [255,255,255], 2)
    return img

def update_tracker(target_detector, image):

    _, bboxes = target_detector.detect_image(image)
    if len(bboxes)==0:
        return image, []
    dets = np.array(bboxes)
    outputs = ocsort.update(dets, image)
    xyxy_bboxes = []
    for value in list(outputs):
        x1, y1, x2, y2, track_id, cls_name, _= value
        # cls_name = target_detector.get_classes_name(cls_id)
        x1, y1, x2, y2, track_id = float(x1), float(y1), float(x2), float(y2), int(track_id)
        xyxy_bboxes.append((x1, y1, x2, y2, cls_name, track_id))
    return image, xyxy_bboxes

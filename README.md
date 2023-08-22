<!--
 * @Description: 
 * @Author: Egrt
 * @Date: 2023-08-22 13:14:38
 * @LastEditors: Egrt
 * @LastEditTime: 2023-08-22 13:24:29
-->
## Eagle—eye：使用YOLOv7+OcSort实现区域入侵检测
---

## 目录
1. [仓库更新 Top News](#仓库更新)
2. [相关仓库 Related code](#相关仓库)
3. [使用教程 Tutorials](#使用教程)
4. [参考资料 Reference](#Reference)


## 相关仓库
| 目标检测模型 | 路径 |
| :----- | :----- |
YoloV7-OBB | https://github.com/Egrt/yolov7-obb
YoloV7-Tiny-OBB | https://github.com/Egrt/yolov7-tiny-obb

## 使用教程
1. 打开YoloSort/AIDetector.py
```
class Detector(BaseDet):
    _defaults = {
        #--------------------------------------------------------------------------#
        #   使用自己训练好的模型进行预测一定要修改model_path和classes_path！
        #   model_path指向logs文件夹下的权值文件，classes_path指向model_data下的txt
        #
        #   训练好后logs文件夹下存在多个权值文件，选择验证集损失较低的即可。
        #   验证集损失较低不代表mAP较高，仅代表该权值在验证集上泛化性能较好。
        #   如果出现shape不匹配，同时要注意训练时的model_path和classes_path参数的修改
        #--------------------------------------------------------------------------#
        "model_path"        : 'YoloSort/yolov7/model_data/yolov7-tiny.onnx',
        #---------------------------------------------------------------------#
        #   输入图片的大小，必须为32的倍数。
        #---------------------------------------------------------------------#
        "input_shape"       : [640, 640],
        #---------------------------------------------------------------------#
        #   只有得分大于置信度的预测框会被保留下来
        #---------------------------------------------------------------------#
        "confidence"        : 0.5,
        #---------------------------------------------------------------------#
        #   非极大抑制所用到的nms_iou大小
        #---------------------------------------------------------------------#
        "nms_iou"           : 0.3,
    }
```
在此处配置模型权重，置信度，iou等参数，然后运行app.py

2. 效果演示
https://www.bilibili.com/video/BV1QP411m7cs

## Reference
https://github.com/WongKinYiu/yolov7

https://github.com/bubbliiiing/yolov7-pytorch

<!--
 * @Description: 
 * @Author: Egrt
 * @Date: 2021-05-08 15:27:48
 * @LastEditors: Egrt
 * @LastEditTime: 2023-03-10 18:49:20
-->
## PyQt5实现目标检测系统搭建——支持多线程
---

## 功能
1. 支持读取本地图片
2. 支持读取本地视频
3. 支持打开摄像头实时检测
4. 支持多线程，防止卡顿
5. 支持检测到人脸未佩戴口罩时记录，并语音警告

## 所需环境
torch==1.2.0
PyQt5==5.15.7
pygame==2.2.0

## 文件下载
模型权重下载后放入**model_data**文件夹中

[yolov4_mobile_mask.pth](https://github.com/Egrt/YOLO_PyQt5/releases/download/V1.0/yolov7_mobile_mask.pth)

## 运行
运行根目录下**main.py**启动界面：

![](maskimg\demo.png)
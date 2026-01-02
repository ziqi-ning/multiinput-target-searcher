# 多输入目标搜索系统 (Multi-Input Target Searcher)

> **注意**: 当前分支是演示版本 (Demo)，完整功能请移步 [formal 分支](../../tree/formal)，该分支包含完整实现和详细文档。

## 项目简介

这是一个基于树莓派Pico和上位机的多输入目标搜索系统，结合了计算机视觉、舵机控制和多种传感器输入，实现了对特定颜色和形状目标的自动识别与跟踪。

## 系统架构

系统由两部分组成：
1. **上位机 (Upper Computer)**: 基于Python的计算机视觉处理单元
2. **下位机 (Pico)**: 基于树莓派Pico的硬件控制单元

## 功能特点

- **多模式目标识别**: 支持圆形、梯形、三角形、杆状等多种形状识别
- **颜色检测**: 支持红、绿、蓝等多种颜色的精确识别
- **实时跟踪**: 基于PID算法的舵机实时跟踪控制
- **多输入支持**: 支持摄像头、按钮、LCD显示等多种输入方式
- **串口通信**: 上位机与下位机通过串口进行高效通信

## 文件结构

```
multiinput-target-searcher/
├── main_upper_computer.py      # 上位机主程序
├── main_pico.py                # Pico下位机主程序
├── main_I2C_scaner.py          # I2C设备扫描程序
├── src_for_upper_computer/     # 上位机源代码目录
│   ├── allin.py               # 综合处理模块
│   ├── colorblob.py           # 颜色检测模块
│   └── outsite.py             # 形状识别模块
└── src_for_pico/              # Pico源代码目录
    ├── pid.py                 # PID控制算法
    ├── servo.py               # 舵机控制
    └── ws2812b.py             # LED灯带控制
```

## 主要模块说明

### 上位机模块

- **allin.py**: 综合处理模块，整合颜色检测和形状识别功能
- **colorblob.py**: 颜色检测模块，支持多种颜色的HSV阈值检测
- **outsite.py**: 形状识别模块，实现圆形、梯形、三角形等形状的识别

### 下位机模块

- **pid.py**: PID控制算法实现，用于舵机精确跟踪
- **servo.py**: 舵机控制封装，提供角度控制和位置控制接口
- **ws2812b.py**: WS2812B LED灯带控制，支持多种颜色和亮度调节

## 硬件要求

- 树莓派Pico
- 舵机 (至少2个，用于X轴和Y轴控制)
- 摄像头
- LCD1602显示屏
- WS2812B LED灯带
- 按钮开关
- 串口通信模块

## 软件依赖

### 上位机
- Python 3.x
- OpenCV
- NumPy
- PySerial

### 下位机
- MicroPython
- RP2040 PIO

## 快速开始

### 上位机运行

```bash
python main_upper_computer.py
```

### 下位机运行

1. 将MicroPython固件刷入树莓派Pico
2. 上传src_for_pico目录下的所有文件
3. 运行main_pico.py

## 工作原理

1. 上位机通过摄像头捕获图像
2. 使用颜色检测和形状识别算法定位目标
3. 计算目标位置与图像中心的偏差
4. 通过串口将位置信息发送给下位机
5. 下位机根据PID算法控制舵机转动，实现对目标的跟踪

## 注意事项

- 当前分支是演示版本，功能可能不完整
- 完整功能请移步 [formal 分支](../../tree/formal)
- 确保串口连接正确，默认使用COM7端口
- 摄像头需正确安装并配置

## 许可证

本项目采用MIT许可证，详见LICENSE文件

## 贡献

欢迎提交Issue和Pull Request来改进项目

## 联系方式

如有问题，请通过Issue联系我
        

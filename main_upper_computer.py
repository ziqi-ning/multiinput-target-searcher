#!/usr/bin/env python3
import cv2
import serial
import upuartuse
import outsite
import colorblob
import allin
from time import sleep
from datetime import datetime

def mouse_callback(event, x, y, flags, param):
    """
    鼠标回调函数
    event: 鼠标事件类型
    x, y: 鼠标坐标
    flags: 鼠标事件标志
    param: 传递的参数
    """
    if event == cv2.EVENT_LBUTTONDOWN:  # 左键点击
        target.x = x
        target.y = y
        target.flag = 1
        print(f"[{datetime.now(). strftime('%Y-%m-%d %H:%M:%S')}] 点击位置: ({target.x}, {target.y})")
                    # 串口包装发送
        package = upuartuse.package_blobs_data(target)
        ser.write(package)

global target, ctr, R
target = upuartuse.TargetCheck()
ctr = upuartuse.ModeCtrl()
R = upuartuse.UartBufParse()

IMAGE_WIDTH = 640
IMAGE_HEIGHT = 480

#______________________________________________________________
def deal_data(cam,ser):
    
    ctr.work_mode=0x00 # 初始空闲模式
    img_update_flag=0
    count = 0

    while(True):

        # count += 5
        img_update_flag=1

        if img_update_flag==1:
            img_update_flag=0
            if ctr.work_mode==0x00:#空闲模式
                ret, frame = cam.read()
                if not ret:
                    print("Can't receive frame (stream end? ).  Exiting...")
                    break

                
                # frame = cv2.resize(frame, (640, 480))
                # frame = cv2.flip(frame, -1)

                
                composite_img, type_list = allin. give_me_a_color_and_i_will_give_you_a_shape(frame, "red", bais=35)

                max_item = max([item for item in type_list if item["type"] == 0], 
                key=lambda x: x["lengh"], 
                default=None)

                if max_item:
                    center = max_item["center"]
                    target.x = center[0]
                    target.y = center[1]
                    target.flag = 1
                    print("target.x:{}, target.y:{}, flag:{}".format(target.x, target.y, target.flag))
                else:
                    target.flag = 0
                    #print("没有找到type为0的元素:{}".format(target.flag))
                package = upuartuse.package_blobs_data(target)
                ser.write(package)


            elif ctr.work_mode==0x01:# 识别圆的模式
                pass
            elif ctr.work_mode==0x02:#听声辩位雷达模式
                pass
            elif ctr.work_mode==0x03:#空闲模式
                pass
            elif ctr.work_mode==0x04:#AprilTag模式
                pass
            elif ctr.work_mode==0x05:#色块模式
                pass
            elif ctr.work_mode==0x06:#条形码
                pass
            elif ctr.work_mode==0x07:#24年真题
                pass
            else:
                pass

            # 读模式码
            upuartuse.uart_data_read(R, ser, ctr)

            cv2.imshow("composite_img", composite_img)
            
            if cv2.waitKey(1) & 0xFF == ord('q'):
                break
    cam.release()
    cv2.destroyAllWindows()
#______________________________________________________________


if __name__ == '__main__':

    global ser, cam
    
    ser = serial.Serial('COM7', 115200, timeout=0.5)
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Cannot open camera")
        exit()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ")
    
    # window_name = "composite_img"
    # cv2.namedWindow(window_name)
    # # 设置鼠标回调函数
    # cv2. setMouseCallback(window_name, mouse_callback)
    deal_data(cam, ser)


    
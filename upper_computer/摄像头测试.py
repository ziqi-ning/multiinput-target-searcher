import numpy as np
import cv2
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
        print(f"[{datetime.now(). strftime('%Y-%m-%d %H:%M:%S')}] 点击位置: ({x}, {y})")

if __name__ == '__main__':
    cam = cv2.VideoCapture(0)
    if not cam.isOpened():
        print("Cannot open camera")
        exit()
    print(f"[{datetime.now().strftime('%Y-%m-%d %H:%M:%S')}] ")
    
    window_name = "composite_img"
    cv2.namedWindow(window_name)
    # 设置鼠标回调函数
    cv2. setMouseCallback(window_name, mouse_callback)
    
    while True:
        ret, frame = cam.read()

        if not ret:
            print("Can't receive frame (stream end? ).  Exiting...")
            break
        
        # composite_img, type_list = allin. give_me_a_color_and_i_will_give_you_a_shape(frame, "blue", bais=30)
        frame = cv2.resize(frame, (640, 480))
        frame = cv2.flip(frame, -1)

        cv2.imshow("composite_img", frame)

        if cv2.waitKey(1) == ord('q'):
            break
        
    cam.release()
    cv2.destroyAllWindows()
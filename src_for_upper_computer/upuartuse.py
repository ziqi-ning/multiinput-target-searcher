# 初始化串口通信模块
# 导入串口通信库和配置文件



class ModeCtrl:   # 控制模式 ctr
    work_mode = 0x01
    check_show = 1


# UART缓冲区解析类定义:R
class UartBufParse:    # 接受并处理好的控制字类
    def __init__(self):
        self.uart_buf = []    # 数据缓冲区
        self._data_len = 0    # 当前数据长度
        self._data_cnt = 0    # 数据计数
        self.state = 0        # 状态机状态
        self.color = 0       # 目标颜色
        self.outlook = 0     # 目标外观


class TargetCheck:    # 初始化的target类
    def __init__(self):
        self.x = 0     # x
        self.y = 0     # y 
        self.flag = 0
        self.color = 0
        self.outlook = 0    

# 串口数据解析函数
# data_buf: 接收到的数据缓冲区
# num: 数据总长度

def Receive_Anl(data_buf,num,ctr, R):
    # 校验和计算
    sum = 0
    i = 0
    while i<(num-1):
        sum = sum + data_buf[i]
        i = i + 1
    sum = sum%256 #取余运算
    # 校验和验证
    if sum != data_buf[num-1]:
        # print("校验失败！有数据为：{}".format(data_buf))
        return
    # 校验通过后的处理
    if data_buf[2]==0xA0:
        # 设置工作模式
        ctr.work_mode = data_buf[4]
        print("校验完毕，模式码是：",ctr.work_mode)
    elif data_buf[2] == 0xB0:  # 坐标数据功能字
        # # 提取x数据（假设大端格式，2字节）
        color = (data_buf[4] << 8) | data_buf[5]
        outlook = (data_buf[6] << 8) | data_buf[7]
        # flag = data_buf[8]
        # print("目标坐标：({},{})\n标志位：{}".format(x,y,flag))
        R.color = color
        R.outlook = outlook
        print("目标颜色：{}\n目标外观：{}".format(color,outlook))
    

# UART数据状态机解析函数
# buf: 当前处理的字节数据
# ctr: 全局控字对象
# R: 全局数据解析对象

def uart_data_prase(R, buf, ctr):  # 处理接受数据
    # 状态机实现：检测协议头0xFF
    # print(format(buf, "X"))
    if R.state==0 and buf==0xFF:#帧头1
        R.state=1
        R.uart_buf.append(buf)
    # 状态机实现：检测协议头0xFE
    elif R.state==1 and buf==0xFE:#帧头2
        R.state=2
        R.uart_buf.append(buf)
    # 状态机实现：读取功能字（命令标识）
    elif R.state==2 and buf<0xFF:#功能字
        R.state=3
        R.uart_buf.append(buf)
    # 状态机实现：读取数据长度
    elif R.state==3 and buf<50:#数据长度小于50
        R.state=4
        R._data_len=buf  #有效数据长度
        R._data_cnt=buf+5#总数据长度
        R.uart_buf.append(buf)
    # 状态机实现：读取有效数据
    elif R.state==4 and R._data_len>0:#存储对应长度数据
        R._data_len=R._data_len-1
        R.uart_buf.append(buf)
        if R._data_len==0:
            R.state=5
    # 状态机实现：读取校验字节
    elif R.state==5:
        R.uart_buf.append(buf)
        R.state=0
        # 调用完整数据包解析函数
        # print("接收到数据包：",R.uart_buf)
        Receive_Anl(R.uart_buf,R.uart_buf[3]+5,ctr,R)
        R.uart_buf=[]#清空缓冲区，准备下次接收数据
    # 状态机异常处理
    else:
        R.state=0
        R.uart_buf=[]#清空缓冲区，准备下次接收数据


# 数据打包函数（用于发送）
# mode: 工作模式
# target: 目标对象（包含多种数据属性）

def package_blobs_data(target):
    # 协议头定义
    HEADER = [0xFF, 0xFE]
    # 构造字节数组数据包
    data = bytearray([HEADER[0], HEADER[1], 0xB0, 0x00,
                      target.x >> 8, target.x & 0xff,
                      target.y >> 8, target.y & 0xff,
                      target.flag >> 8,target.flag & 0xff,
                      target.color >> 8,target.color & 0xff,
                      target.outlook >> 8,target.outlook & 0xff,
                      0x00])
    # 计算数据包长度并更新长度字段
    data_len = len(data)
    data[3] = data_len - 5
    # 计算校验和（除最后一位外的所有字节和）
    checksum = sum(data[:-1]) & 0xff
    # 设置校验位
    data[-1] = checksum
    return data

def uart_data_read(R, ser, ctr):
    buf_len=ser.in_waiting
    if buf_len>0:
        buf=ser.read(buf_len)
        print("serial buf :",buf)
        for i in range(0,buf_len):
            uart_data_prase(R, buf[i], ctr)

import machine
import utime
import ws2812b
import uartuse
from servo import Servo
from time import sleep
from i2c_lcd import I2cLcd
import binascii
import pid

strip = ws2812b.ws2812b(4,0,22)

DEFAULT_I2C_ADDR = 0x27

RED = (255, 0, 0)
ORANGE = (255, 165, 0)
YELLOW = (255, 150, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
INDIGO = (75, 0, 130)
VIOLET = (138, 43, 226)
COLORS = (RED, ORANGE, YELLOW, GREEN, BLUE, INDIGO, VIOLET)


class Menu:
    def __init__(self):
        self.color = 0
        self.outlook = 0
        self.color_dict = {0:'RED', 1:'BLUE', 2:'GREEN'}
        self.outlook_dict = {0:'Cricel', 1:'Recttangle', 2:'Triangle'}
    
    def show_menu(self):
        info_str = self.color_dict[self.color] + " " + self.outlook_dict[self.outlook]
        showinfo(info_str)
        

    def update_color(self, type):
        if type == 'plus':
            self.color = self.color+1
        elif type =='minus':
            self.color = self.color-1
        else:
            print("wrong type")
            return
        if self.color < 0:
            self.color = 2
        if self.color > 2:
            self.color = 0
        target.x = self.color
        uart0.send()
        self.show_menu()

    def update_outlook(self, type):
        if type == 'plus':
            self.outlook = self.outlook+1
        elif type =='minus':
            self.outlook = self.outlook-1
        else:
            print("wrong type")
            return
        if self.outlook < 0:
            self.outlook = 2
        if self.outlook > 2:
            self.outlook = 0
        target.y = self.outlook
        uart0.send()
        self.show_menu()

class Uart:
    def __init__(self, uart_num=0, baudrate=115200, tx_pin=0, rx_pin=1):
        self.uart_num = uart_num
        self.baudrate = baudrate
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.uart = machine.UART(uart_num, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def send(self):
        package = uartuse.package_blobs_data(target)
        self.uart.write(package)
        print("had sent: {}".format(package))

    def recv(self):
        if self.uart.any():
            data = self.uart.read(self.uart.any())
            hex_str = binascii.hexlify(data).decode('utf-8')
#             print("have received: ", hex_str)
            uartuse.uart_data_prase(R, data[0], ctr)


class servo:
    def __init__(self, pin, minVal=2500, maxVal=7500):
        #验证参数
        validate = lambda min_val, max_val: (
            isinstance(min_val, int) and isinstance(max_val, int) and
            min_val >= 0 and max_val >= 0 and
            min_val < max_val
        )
        if not validate(minVal, maxVal):
            raise ValueError("minVal和maxVal必须是大于等于0的整数，且minVal必须小于maxVal")
        
        self.reality = Servo(pin)
        self.min = minVal
        self.max = maxVal
        self.servo_Angle(90)
        sleep(0.25)
        self.reality.free()

    # 映射
    def makerobo_map(self, x, in_min, in_max, out_min, out_max):
        return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
    
    # 把范围值转化为角度值
    def servo_Angle(self, angle):
        if angle < 0:
            angle = 0
        if angle > 180:
            angle = 180
        self.reality.goto(round(self.makerobo_map(angle,0,180,0,1024)))
        sleep(0.25)
        self.reality.free()

    def servo_any(self, value):
        if value < self.min:
            value = self.min
        if value > self.max:
            value = self.max
        self.reality.goto(round(self.makerobo_map(value,self.min,self.max,0,1024)))
        sleep(0.25)
        self.reality.free()





class button_foundamation:
    def __init__(self, name, number): # 引脚在此输入GPIO
        self.name = name
        self.number = number
        self.pin = machine.Pin(number, machine.Pin.IN, machine.Pin.PULL_UP)
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler= lambda pin: self.default_irq_handler(pin))

    def default_irq_handler(self, pin):
        print("default Button {} pressed".format(self.name))

    def new_irq(self, irq_handler):
        self.pin.irq(trigger=machine.Pin.IRQ_FALLING, handler=lambda pin: irq_handler(pin))
        print("Button {} irq changed and number to {}".format(self.name, self.number))

    def irq_handler(self, pin):  # 重写这个方法以改成自己的irq处理函数
        print("wait for change new irq:  {} pressed".format(self.name))

    def deinit(self):
        self.pin.deinit()

class button_LED(button_foundamation):
    def __init__(self, name, number, led_pin, led_color = 'RED'):
        super().__init__(name, number)
        self.led_pin = led_pin
        self.led_color = led_color
        self.new_irq(self.led_irq_handler)

    def led_irq_handler(self, pin):
        strip.set_pixel(self.led_pin, self.led_color[0], self.led_color[1], self.led_color[2])
        # sleep(0.01)
        strip.show()
        sleep(0.25) # 中断里面尽量不要延时
        showinfo("{} Button pressed".format(self.name))
        strip.set_pixel(self.led_pin, 0, 0, 0)
        strip.show()

class button_menu(button_foundamation):
    def __init__(self, name, number, choice, type):
        super().__init__(name, number)
        self.choice = choice
        self.type = type
        self.new_irq(self.menu_irq_handler)

    def menu_irq_handler(self, pin):
        if self.choice == 'color':
            menu.update_color(self.type)
        elif self.choice == 'outlook':
            menu.update_outlook(self.type)
        else:
            print("choice error")


# 初始化LCD1602液晶模块，全局的
def makerobo_setup():
    global lcd 
    i2c = machine.I2C(1,sda=machine.Pin(2),scl=machine.Pin(3),freq=400000) #GPIO的0和1号引脚，0是SCL,1是SDA
    lcd = I2cLcd(i2c, DEFAULT_I2C_ADDR, 2, 16)  # 初始化(设备地址, 背光设置)
    lcd.putstr("Hello!!! \nMakerobo kit")       # 显示第一行信息及第二行信息
    sleep(0.75)                                    # 延时2S

def showinfo(info):
    lcd.clear()   
    if isinstance(info, str):                            # 清除显示
        tmp_info = info[:32]
        lcd.putstr(tmp_info)    
    else:
        print("type error need str")

if __name__ == '__main__':

    global menu
    global uart
    global target
    global ctr
    global R

    menu = Menu()
    target = uartuse.TargetCheck()
    ctr = uartuse.ModeCtrl()
    R = uartuse.UartBufParse()

    uart0 = Uart()

    makerobo_upPin = 21    #轻触按键Pin端口
    makerobo_leftPin = 20  #轻触按键Pin端口
    makerobo_downPin = 19  #轻触按键Pin端口
    makerobo_rightPin = 18 #轻触按键Pin端口

    # makerobo_up = button_real("makerobo_up", makerobo_upPin)
    # makerobo_left = button_real("makerobo_left", makerobo_leftPin)
    # makerobo_down = button_real("makerobo_down", makerobo_downPin)
    # makerobo_right = button_real("makerobo_right", makerobo_rightPin)

    # makerobo_up = button_LED("makerobo_up", makerobo_upPin, 0, GREEN)
    # makerobo_left = button_LED("makerobo_left", makerobo_leftPin, 1, BLUE)
    # makerobo_down = button_LED("makerobo_down", makerobo_downPin, 2, YELLOW)
    # makerobo_right = button_LED("makerobo_right", makerobo_rightPin, 3, RED)

    makerobo_up = button_menu("makerobo_up", makerobo_upPin, 'color', 'plus')
    makerobo_left = button_menu("makerobo_left", makerobo_leftPin, 'outlook', 'minus')
    makerobo_down = button_menu("makerobo_down", makerobo_downPin, 'color', 'minus')
    makerobo_right = button_menu("makerobo_right", makerobo_rightPin, 'outlook','plus')

    makerobo_setup()

    servo_up_y = servo(17, 0, 480)       # 舵机管脚接在GP2，宽480
    servo_down_x = servo(16, 0, 640)       # 舵机管脚接在GP3，高640

    # servo_up.servo_any(90)
    # servo_down.servo_any(90)

    # 【重点】创建PID控制器
    # PIDController(竖直舵机, 水平舵机, kp, ki, kd)
    pid_ctrl = pid.PIDController(servo_up_y, servo_down_x, 
                        kp=0.2, ki=0.01, kd=0.01)

    while True:

        for i in range(32):
            uart0.recv()

        if ctr.found_flag:
            # 【重点】update方法需要4个坐标参数
            # update(目标X, 目标Y, 当前X, 当前Y, 是否找到目标)
            pid_ctrl.update(
                320,           # 目标X坐标（0-640像素）
                240,           # 目标Y坐标（0-480像素）
                ctr.x_now,          # 当前X坐标（0-640像素）
                ctr.y_now,          # 当前Y坐标（0-480像素）
                ctr.found_flag      # 是否找到目标（True/False）
            )
            if uart0.uart.any():
                uart0.uart.read(uart0.uart.any())



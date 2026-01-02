from ssd1306 import SSD1306_I2C
from machine import I2C,Pin,PWM,Timer,UART
from menu import MenuController
from math import ceil
from servo import Servo
import uartuse
import time, utime, sys
import random
import binascii
import pid
import Music
import games

SCREEN_WIDTH = 128
SCREEN_HEIGHT = 64
OLED_I2C_ADDR = 0x3C

# snake config
SNAKE_PIECE_SIZE = 3
MAX_SNAKE_LENGTH = 150
MAP_SIZE_X = 20
MAP_SIZE_Y = 20
START_SNAKE_SIZE = 10
SNAKE_MOVE_DELAY = 5

def toggle():
    global player_switch
    player_switch = not player_switch 
    return player_switch



"""UART"""
class Uart:
    def __init__(self, uart_num=0, baudrate=115200, tx_pin=0, rx_pin=1):
        self.uart_num = uart_num
        self.baudrate = baudrate
        self.tx_pin = tx_pin
        self.rx_pin = rx_pin
        self.uart = UART(uart_num, baudrate=baudrate, tx=machine.Pin(tx_pin), rx=machine.Pin(rx_pin))

    def send(self):
        package = uartuse.package_blobs_data(target)
        self.uart.write(package)
        print("had sent: {}".format(package))

#     def recv(self):
#         if self.uart.any():
#             data = self.uart.read(self.uart.any())
#             hex_str = binascii.hexlify(data).decode('utf-8')
#             # print("have received: ", hex_str)
#             uartuse.uart_data_prase(R, data[0], ctr)

    def recv(self):
        if self.uart.any():
            data = self.uart.read(self.uart.any())
            hex_str = binascii.hexlify(data).decode('utf-8')
            # print("have received: ", hex_str)
            for b in data:
                uartuse.uart_data_prase(R, b, ctr)



"""ENCODER"""
class RotaryEncoder:
    def __init__(self, pin_a, pin_b, pin_sw):
        self.pin_a = Pin(pin_a, Pin.IN)
        self.pin_b = Pin(pin_b, Pin.IN)
        self.pin_sw = Pin(pin_sw, Pin.IN)
        self.position = 0
        self.last_position = 0
        self.b_level = 0
        self.pin_a.irq(trigger=Pin.IRQ_RISING | Pin.IRQ_FALLING, handler=self.encoder_handler)
        self.pin_sw.irq(trigger=Pin.IRQ_FALLING, handler=self.button_handler)
        self.last_time = time.ticks_ms()
    def encoder_handler(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_time) < 2:
            return
        a_current = self.pin_a.value()
        if a_current == 0:
            self.b_level = 0
            if self.pin_b.value() == 1:
                self.b_level = 1
        elif a_current == 1:
            b_current = self.pin_b.value()
            if self.b_level == 1 and b_current == 0:
                self.position -= 1
            elif self.b_level == 0 and b_current == 1:
                self.position += 1
        self.last_time = current_time
    def get_position(self):
        return self.position
    def reset_position(self):
        self.position = 0
        self.last_position = 0
    def button_handler(self, pin):
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_time) > 10:
            # 旋转编码器按键中断任务
#             self.reset_position()  # 重置光标位置，可注释
            
            menu.ensure_cursor()
            self.last_time = current_time



"""SERVO"""
class ServoController:
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
        time.sleep(0.25)
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
        time.sleep(0.25)
        self.reality.free()

    def servo_any(self, value):
        if value < self.min:
            value = self.min
        if value > self.max:
            value = self.max
        self.reality.goto(round(self.makerobo_map(value,self.min,self.max,0,1024)))
        time.sleep(0.25)
        self.reality.free()



"""MUSIC"""



"""GAME"""
class Manual:
    def __init__(self, step=30):
        # 按键引脚定义（根据实际硬件修改）
        LEFT_SW_PIN = 6     # 左按键
        RIGHT_SW_PIN = 7    # 右按键
        UP_SW_PIN = 9       # 上按键
        DOWN_SW_PIN = 8     # 下按键
        self.step = 30               # 每次移动的步长
        self.last_time = 0           # 防抖时间记录
        self.debounce_delay = 200    # 防抖延迟(ms)
        Pan_angle = 90  # 水平初始角度（中间位置）
        Tilt_angle = 90
        self.left_sw = machine.Pin(LEFT_SW_PIN, machine.Pin.IN)
        self.right_sw = machine.Pin(RIGHT_SW_PIN, machine.Pin.IN)
        self.up_sw = machine.Pin(UP_SW_PIN, machine.Pin.IN)
        self.down_sw = machine.Pin(DOWN_SW_PIN, machine.Pin.IN)
        self.servo_Tilt = ServoController(15, 0, 480)       # 舵机管脚接在GP14，宽480
        self.servo_Pan = ServoController(14, 0, 640)       # 舵机管脚接在GP15，高640
        # 设置中断触发方式（下降沿触发，按键按下时）
        self.left_sw.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.left_handler)
        self.right_sw.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.right_handler)
        self.up_sw.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.up_handler)
        self.down_sw.irq(trigger=machine.Pin.IRQ_FALLING, handler=self.down_handler)
    def debounce_check():
        """按键防抖检查"""
        current_time = time.ticks_ms()
        if time.ticks_diff(current_time, self.last_time) > self.debounce_delay:
            self.last_time = current_time
            return True
        return False

    def left_handler(pin):
        """左按键中断处理"""
        if debounce_check():
            global Pan_angle
            Pan_angle = max(5, Pan_angle - self.step)

    def right_handler(pin):
        """右按键中断处理"""
        if debounce_check():
            global Pan_angle
            Pan_angle = min(180, Pan_angle + self.step)
    def down_handler(pin):
        """上按键中断处理"""
        if debounce_check():
            global Tilt_angle 
            Tilt_angle= min(Tilt_angle+self.step,175)

    def up_handler(pin):
        """下按键中断处理"""
        if debounce_check():
            global Tilt_angle 
            Tilt_angle = max(5,Tilt_angle- self.step)    
    def run():
        self.servo_Tilt.servo_Angle(Tilt_angle)
        self.servo_Pan.servo_Angle(Pan_angle)
        time.sleep(0.1)
    
    
    
    
    
"""菜单定义: 菜单项内容与层级关系"""
# [0]home
menu_home = [
    ("------HOME------", ""),
    ("> Pan&Tilt", "current_menu = menu_home_PTZ"),
    ("> Music", "current_menu = menu_home_Music"),
    ("> Game", "current_menu = menu_home_Game"),
    ("< EXIT", "sys.exit()"),
]

# [1]home.PTZ
menu_home_PTZ = [
    ("------PTZ-------", ""),
    ("< BUCK", "current_menu = menu_home"),
    ("> Auto", "current_menu = menu_home_PTZ_Auto"),
    ("> Manual", "current_menu = menu_home_PTZ_Manual"),
]
# [1]home.PTZ.Auto
menu_home_PTZ_Auto = [
    ["------Auto------", ""],
    ["< BUCK", "current_menu = menu_home_PTZ"],
    ["> OFF", "PTZ_select()"],
    ["> Color RED", "color_select()"],
    ["> Shape Cricel", "shape_select()"],
]
menu_home_PTZ_Manual= [
    ["-----Manual-----", ""],
    ["< BUCK", "current_menu = menu_home_PTZ"],
    ["> OFF", ""],
    ["> Pan_angle", ""],
    ["> Tilt_angle", ""],
]
def PTZ_select():
    global PTZ_switch, target, shape, color
    PTZ_switch = (PTZ_switch + 1) % 2
    if PTZ_switch:
        menu_home_PTZ_Auto[2] = ["> ON", "PTZ_select()"]
        target.y = shape
        target.x = color
        uart0.send()
#         flag = "PTZ"
    else:
        menu_home_PTZ_Auto[2] = ["> OFF", "PTZ_select()"]
#         flag = None
def color_select():
    global color
    color = (color + 1) % 3
    menu_home_PTZ_Auto[3] = [f"> Color {color_list[color]}", "color_select()"]  # 重新覆写菜单列表，解决静态菜单问题
def shape_select():
    global shape
    shape = (shape + 1) % 3
    menu_home_PTZ_Auto[4] = [f"> Shape {shape_list[shape]}", "shape_select()"]

# [2]home.Music
menu_home_Music = [
    ("-----MUSIC------", ""),
    ("< BUCK", "current_menu = menu_home"),
    ("> Buzz", "current_menu = menu_home_Music_Buzz"),
    ("> PWM Audio", ""),
]
# home.Music.Buzz
menu_home_Music_Buzz = [
    ("---MUSIC.BUZZ---", ""),
    ("< BUCK", "current_menu = menu_home_Music"),
    ("> Library", "current_menu = menu_home_Music_Buzz_Library"),
    ("> Play", "current_menu = menu_home_Music_Buzz_Play"),
]
# home.Music.Buzz.Library
menu_home_Music_Buzz_Library = [
    ("-MUSIC.BUZZ.LIB-", ""),
    ("< BUCK", "music_close()"),
    ("> 1.happy birthday", "music_select(Music.happy_birthday)"),
    ("> 2.little star", "music_select(Music.little_star)"),
    ("> 3.ode to joy", "music_select(Music.ode_to_joy)"),
    ("> 4.jingle bells", "music_select(Music.jingle_bells)"),
    ("> 5.mary lamb", "music_select(Music.mary_lamb)"),
    ("> 6.super mario", "music_select(Music.super_mario)"),
    ("> 7.chord progression", "music_select(Music.chord_progression)"),
]
# home.Music.Buzz.Play
menu_home_Music_Buzz_Play = [
    ("-MUSIC.BUZZ.PLAY", ""),
    ("< BUCK", "current_menu = menu_home_Music_Buzz"),
    ("> ", ""),
    ("> ", ""),
]

# [3]home.Game
menu_home_Game = [
    ("------GAME------", ""),
    ("< BUCK", "current_menu = menu_home"),
    ("> Greedy Snake", "game()"),
]
# 菜单项函数
def func():
    print("here is your function")
    led.toggle()  # 测试：翻转led
# 游戏入口
def game():
    global flag
    flag = "game"

# 音乐管理器：每次进入都会使该首歌的标志位翻转
def music_select(music):
    global player_movement, player_switch
    player_movement = music  # 切换乐谱
    toggle()
    if player_switch == True:
        player.set_volume(2.3)
        player.play()
    else:
        player.set_volume(0)
        player.stop()  # 停止播放并释放资源
def music_close():  # 本质原因是当回到BUZZ菜单时需要执行多条函数，而使用分号作为多段代码的分割在这里不奏效
    global current_menu
    player.stop()  # 停止播放并释放资源
    current_menu = menu_home_Music_Buzz  # 回到上级菜单
    
# 清串口缓冲区
def flush_uart(uart):
    while uart.any():
        uart.read(uart.any())


if __name__ == "__main__":
    """基础类初始化"""
    target = uartuse.TargetCheck()
    ctr = uartuse.ModeCtrl()
    R = uartuse.UartBufParse()
    uart0 = Uart()
    # led
    led = Pin(25, Pin.OUT)
    # encoder
    encoder = RotaryEncoder(pin_a=12, pin_b=13, pin_sw=11)
    # key
    UP_PIN = machine.Pin(9, machine.Pin.IN)
    DOWN_PIN = machine.Pin(8, machine.Pin.IN)
    RIGHT_PIN = machine.Pin(7, machine.Pin.IN)
    LEFT_PIN = machine.Pin(6, machine.Pin.IN)
    # oled
    SCREEN_WIDTH = 128
    SCREEN_HEIGHT = 64
    OLED_I2C_ADDR = 0x3C
    i2c = I2C(1, scl=Pin(3), sda=Pin(2), freq=400000)
    oled = SSD1306_I2C(SCREEN_WIDTH, SCREEN_HEIGHT, i2c, addr=OLED_I2C_ADDR)
    def reset_oled():
        oled.fill(0)  # 清屏
        oled.show()  # 刷新显示
        
    """拓展类初始化"""   
    # menu
    menu = MenuController(oled, 0, 0, 128, 64, char_height=10)
    cursor = 0
    current_menu = menu_home
    flag = None  # 死循环标志位
    # [0] color
    PTZ_switch = 0
    color = 0
    shape = 0
    color_list = ["RED", "BLUE", "GREEN"]
    shape_list = ["Cricel", "Recttangle", "Triangle"]
    # [1]servo
    servo_up_y = ServoController(15, 0, 480)       # 舵机管脚接在GP14，宽480
    servo_down_x = ServoController(14, 0, 640)       # 舵机管脚接在GP15，高640
    pid_ctrl = pid.PIDController(servo_up_y, servo_down_x, kp=0.15, ki=0, kd=0.05)
    # [2]music
    player_movement = None  # 乐章选择
    player_switch = False  # 播放器开关（默认关闭）
    player = Music.MusicPlayer(  # 创建播放器
                looping = True,
                tempo = 5,
                volume = 0.023,
                pins = [Pin(17)],  # 蜂鸣器: GP17
                auto_play = False
            )
    # [3]game
    snake = games.Snake(oled,UP_PIN,DOWN_PIN,LEFT_PIN,RIGHT_PIN)
    move_time = 0
    manual=Manual()


    while True:
        ctr.found_flag = False
        uart0.recv()
        if ctr.found_flag:
            # 【重点】update方法需要4个坐标参数
            # update(目标X, 目标Y, 当前X, 当前Y, 是否找到目标)
            pid_ctrl.update(
                ctr.x_now,          # 当前X坐标（0-640像素）
                ctr.y_now,          # 当前Y坐标（0-480像素）
                320,           # 目标X坐标（0-640像素）
                240,           # 目标坐标（0-480像素）
                ctr.found_flag      # 是否找到目标（True/False）
            )
            ctr.x_now = 320
            ctr.y_now = 240
            
#         print("ctr.x:{},ctr.t:{}".format(ctr.x_now,ctr.y_now))
            
        flush_uart(uart0.uart)
        """更新当前菜单"""
        menu.show_menu(current_menu)

        """更新光标位置"""
        cursor = encoder.get_position()
        current_menu = current_menu or []
        cursor = (cursor + 1) % len(current_menu)
        cursor = (cursor - 1) % len(current_menu) + 1
        
        """更新光标显示"""
        print(cursor)
        menu.goto_cursor(cursor)
        
        """刷新显示"""
        oled.show()  # 刷新显示
        # time.sleep(0.001)  # 短暂延时，降低CPU使用率

        """循环任务"""
        while(flag == "game"):
            if snake.game_state == games.State.START:  # 游戏开始
                snake.game_state = games.State.RUNNING
            elif snake.game_state == games.State.RUNNING:  # 游戏运行
                move_time += 1
                snake.read_direction()
                if move_time >= SNAKE_MOVE_DELAY:
                    snake.direction = snake.new_direction
                    snake.oled.fill(0)
                    if not snake.move_snake():
                        snake.game_state = games.State.GAMEOVER
                        snake.show_game_over()
#                         time.sleep(1)
                    snake.draw_map()
                    snake.show_score()
                    snake.oled.show()
                    snake.check_fruit()
                    move_time = 0
            elif snake.game_state == games.State.GAMEOVER:  # 游戏结束
                flag = None  # 退出游戏循环
                current_menu = menu_home_Game  # 退回的菜单为游戏子菜单
                snake = games.Snake(oled,UP_PIN,DOWN_PIN,LEFT_PIN,RIGHT_PIN)
                snake.game_state = games.State.START
                time.sleep(1)  # 停留展示game over界面
            time.sleep_ms(20)
            oled.show()  # 刷新显示
 
        
        
        """调试"""
#         print(player_movement, player_switch)
#         print(color)
#         print(color_list[color])



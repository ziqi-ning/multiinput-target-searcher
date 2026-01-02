"""
PID控制器 - 用于舵机跟踪目标
输入：像素坐标偏差
输出：舵机控制信号

硬件配置：
- servo_y: Y轴舵机，范围0-480
- servo_x: X轴舵机，范围0-640
"""

import utime

class PIDController:
    def __init__(self, servo_y, servo_x, kp=0.8, ki=0.03, kd=0.2):
        """
        初始化PID控制器
        
        参数：
        - servo_y: Y轴舵机（上下动）
        - servo_x: X轴舵机（左右动）
        - kp: 比例系数
        - ki: 积分系数
        - kd: 微分系数
        """
        self.servo_y = servo_y  # Y轴舵机
        self.servo_x = servo_x  # X轴舵机
        
        # PID参数
        self.kp = kp
        self.ki = ki
        self.kd = kd
        
        # 误差积分
        self.integral_x = 0
        self.integral_y = 0
        
        # 上一次误差（用于计算微分）
        self.last_error_x = 0
        self.last_error_y = 0
        
        # ===== 关键：坐标系统映射 =====
        # 图像框大小
        self.image_width = 640    # 图像X最大值
        self.image_height = 480   # 图像Y最大值
        self.image_center_x = self.image_width / 2      # 320
        self.image_center_y = self.image_height / 2     # 240
        
        # 【舵机范围】servo_any接收的范围是 0-480 和 0-640
        self.servo_x_min = 0
        self.servo_x_max = 640    # X轴范围是0-640
        self.servo_y_min = 0
        self.servo_y_max = 480    # Y轴范围是0-480
        
        self.servo_center_x = self.servo_x_max / 2  # 320
        self.servo_center_y = self.servo_y_max / 2  # 240
        
        # 舵机当前位置 - 从中心开始
        self.current_x = self.servo_center_x  # 320
        self.current_y = self.servo_center_y  # 240
        
        # PID输出限制（防止饱和）
        self.output_limit = 100  # 每次最大转动量
        
        print("PID Controller initialized")
        print("Image size: {}x{}".format(self.image_width, self.image_height))
        print("Servo X range: {}-{}".format(self.servo_x_min, self.servo_x_max))
        print("Servo Y range: {}-{}".format(self.servo_y_min, self.servo_y_max))
        print("Current position: X={}, Y={}".format(int(self.current_x), int(self.current_y)))
    
    def _clamp(self, value, min_val, max_val):
        """限制值在范围内"""
        if value < min_val:
            return min_val
        if value > max_val:
            return max_val
        return value
    
    def _pid_calculate(self, error, integral, last_error):
        """
        PID计算（单轴）
        """
        # 比例项
        p_out = self.kp * error
        
        # 积分项（累积误差）
        integral += error
        # 积分项限制，防止积分饱和
        integral = self._clamp(integral, -500, 500)
        i_out = self.ki * integral
        
        # 微分项（误差变化率）
        derivative = error - last_error
        d_out = self.kd * derivative
        
        # 总输出
        output = p_out + i_out + d_out
        
        return output, integral
    
    def update(self, target_x, target_y, current_x, current_y, found_flag):
        """
        更新PID控制器并控制舵机
        
        参数：
        - target_x: 目标X坐标（像素，0-640）
        - target_y: 目标Y坐标（像素，0-480）
        - current_x: 当前X坐标（像素，0-640）
        - current_y: 当前Y坐标（像素，0-480）
        - found_flag: 是否找到目标
        """
        if not found_flag:
#             print("Target not found, PID paused")
            # 【新增】没找到目标时，重置
            self.integral_x = 0
            self.integral_y = 0
            self.last_error_x = 0
            self.last_error_y = 0
            return
        
        # 计算误差（像素偏差）
        # error_x = current_x - target_x 
        error_x = target_x - current_x
        error_y = current_y - target_y
        # error_y = target_y - current_y
        
        # PID计算
        pid_x, self.integral_x = self._pid_calculate(
            error_x, self.integral_x, self.last_error_x
        )
        pid_y, self.integral_y = self._pid_calculate(
            error_y, self.integral_y, self.last_error_y
        )
        
        # 保存本次误差用于下次微分
        self.last_error_x = error_x
        self.last_error_y = error_y
        
        # 更新舵机位置
        self.current_x += pid_x
        self.current_y += pid_y
        
        # 【重点】限制舵机范围（根据硬件）
        self.current_x = self._clamp(self.current_x, self.servo_x_min, self.servo_x_max)
        self.current_y = self._clamp(self.current_y, self.servo_y_min, self.servo_y_max)
        
        # 控制舵机转动
        self.servo_x.servo_any(self.current_x)  # X轴（0-640）
        self.servo_y.servo_any(self.current_y)  # Y轴（0-480）
        
        # 调试输出
        print("Error: ({:4d}, {:4d}) | PID: ({:6.1f}, {:6.1f}) | Servo: X={:4d}, Y={:4d}".format(
            error_x, error_y, pid_x, pid_y, int(self.current_x), int(self.current_y)))
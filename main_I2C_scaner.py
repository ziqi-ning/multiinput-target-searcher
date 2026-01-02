"""
第7章：I2C总线基础与传感器初步演示
- I2C扫描所有设备
- 读取一个寄存器（如WHO_AM_I）
注意：
实际硬件需有外部设备或模块(如MPU6050,nRF24/DS18B20等)，以下为标准用法。
"""

import machine
import utime

def i2c_demo():
    i2c = machine.I2C(0, scl=machine.Pin(1), sda=machine.Pin(0), freq=100000)
    devices = i2c.scan()
    print("I2C总线发现设备地址：\n",[hex(d) for d in devices])
    count = 0
    if not devices:
        print("未检测到I2C设备，无真实演示")
    for d in devices:
        addr = d
        try:
            # 以WHO_AM_I为例读取设备ID
            data = i2c.readfrom_mem(addr, 0x75, 1)
            print("设备({}) ID: 0x{:02X}".format(hex(addr),data[0]))
        except Exception as e:
            print("读取寄存器失败:", e)
        count+=1


if __name__ == "__main__":
    i2c_demo()
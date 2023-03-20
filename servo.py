# -*- coding: utf-8 -*-

# -----------------------------------------------------------
# RCサーボモータ用ライブラリ
# -----------------------------------------------------------
# 2019/12/30    修正,動作確認
# -----------------------------------------------------------

import pigpio
import subprocess

class servo:

    pi = pigpio.pi()

    servo_pin = 0

    angle_min = -90.0
    angle_max = 90.0
    width_min = 500
    width_max = 2400

    angle_data = 0.0
    width = 1500

    def init(self, pin, **data):
        self.servo_pin = pin
        self.pi.set_mode(self.servo_pin, pigpio.OUTPUT)
        self.set_angle(0)
        if 'width_min' in data:
            self.width_min = data['width_min']
        if 'width_max' in data:
            self.width_max = data['width_max']
        if 'angle_min' in data:
            self.angle_min = data['angle_min']
        if 'angle_max' in data:
            self.angle_max = data['angle_max']
        # subprocess.run(['sudo', 'pigpiod'])

    def end(self):
        self.set_angle(0)
        from time import sleep
        sleep(0.1)
        self.pi.set_mode(self.servo_pin, self.pigpio.INPUT)
        #self.pi.stop() # ファイナライズ

    def home_position(self):
        center_width = (self.width_max + self.width_min) /2
        self.pi.set_servo_pulsewidth(self.servo_pin, center_width)

    def set_angle(self, angle):
        if self.angle_min <= angle <= self.angle_max:
            self.angle_data = angle
            self.update_servo()
            return True
        else:
            print(str(angle) + " is out of range")
            return False

    def angle_inc(self, angle):
        if self.angle_min <= self.angle_data + angle <= self.angle_max:
            self.angle_data += angle
            self.update_servo()

    def angle_dec(self, angle):
        if self.angle_min <= self.angle_data - angle <= self.angle_max:
            self.angle_data -= angle
            self.update_servo()           
        
    def update_servo(self):
        angle_range = self.angle_max - self.angle_min
        width_range = self.width_max - self.width_min
        absolute_angle = self.angle_data - self.angle_min
        self.width = self.width_min + absolute_angle * (width_range / angle_range)
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width)

    def calibration(self):

        print("===== calibration =====")
        
        self.pi.set_servo_pulsewidth(self.servo_pin, self.width_min)
        print("Please input now angle (min): ")
        self.angle_min = float(input())

        self.pi.set_servo_pulsewidth(self.servo_pin, self.width_max)
        print("please input now angle (max):")
        self.angle_max = float(input())

        print("angle max = " + str(self.angle_max))
        print("angle min = " + str(self.angle_min))

        print("=======================")


if __name__ == '__main__':

    servo_PIN = 26

    servo = servo()
    servo.init(servo_PIN, angle_min=-90.0, angle_max=90.0)

    servo.set_angle(0)

    try:

        print("Please input angle")

        while True:
            
            angle = int(input('angle:'))
            servo.set_angle(angle)

    except KeyboardInterrupt:
        pass

    finally:
        servo.end()
        servo.pi.stop()
        
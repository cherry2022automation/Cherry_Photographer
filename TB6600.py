# -*- coding: utf-8 -*-

# ----------------------------------

# ----------------------------------

import RPi.GPIO as GPIO
from time import sleep

class TB6600():

    # GPIO
    enable_pin = 2
    direction_pin = 3
    pulse_pin = 4

    pulse_high = GPIO.HIGH
    pulse_low = GPIO.LOW
    enable_en = GPIO.HIGH
    enable_dis = GPIO.LOW
    direction_CW = GPIO.HIGH
    direction_CCW = GPIO.LOW

    direction = 'CW'

    # motor
    step_angle = 1.8
    step_split = 4

    def __init__(self, **option):
        if 'enable_pin' in option:
            self.enable_pin = option['enable_pin']
        if 'direction_pin' in option:
            self.direction_pin = option['direction_pin']
        if 'pulse_pin' in option:
            self.pulse_pin = option['pulse_pin']
        if 'step_angle' in option:
            self.step_angle = option['step_angle']
        if 'step_split' in option:
            self.step_split = option['step_split']


        self.angle_1pulse = self.step_angle /self.step_split           # [°/pulse]
        self.Rotational_pulse = 360/self.angle_1pulse

        self.emergency = False

    def emergency(self):
        print('ここは実行されてるよ')
        self.emergency = True

    def init(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.enable_pin, GPIO.OUT)
        GPIO.setup(self.direction_pin, GPIO.OUT)
        GPIO.setup(self.pulse_pin, GPIO.OUT)
        self.def_direction("CW")
        self.enable(False)

    def end(self):
        self.enable(False)
        GPIO.cleanup()

    def calc_pulse_interval(self, rotational_speed_s):
        # around_pulses = 360 / angle_1pulse            # [pulse/rev]
        angular_velocity = rotational_speed_s * 360     # [°/s]
        pulse_speed = angular_velocity / self.angle_1pulse   # [pulse/s]
        pulse_period = 1 / pulse_speed                  # [pulse]
        pulse_interval = pulse_period / 2
        return pulse_interval

    def output_pulse_r(self, num, rotational_speed_s):

        interval = self.calc_pulse_interval(rotational_speed_s)
        
        for i in range(num):
            if self.emergency == True:
                return -1
            self.output_one_pulse(interval)
        return 0

    def output_pulse_p(self, num, pulse_speed):

        interval = (1/pulse_speed) / 2
        
        for i in range(num):
            if self.emergency == True:
                return -1
            self.output_one_pulse(interval)
        return 0

    def output_one_pulse(self, interval):
        if self.emergency == True:
            return -1
        GPIO.output(self.pulse_pin, self.pulse_high)
        sleep(interval)
        GPIO.output(self.pulse_pin, self.pulse_low)
        sleep(interval)
        return 0

    def def_direction(self, dir):
        if dir == "CW":
            GPIO.output(self.direction_pin, self.direction_CW)
            self.direction = "CW"
        elif dir == "CCW":
            GPIO.output(self.direction_pin, self.direction_CCW)
            self.direction = "CCW"

    def enable(self, bool):
        if bool == True:
            GPIO.output(self.enable_pin, self.enable_en)
        elif bool == False:
            GPIO.output(self.enable_pin, self.enable_dis)

    def trapezoid_pulse_p(self, pulse_num, ini_pulse_speed, max_pulse_speed, acceleration_time):
        pulse_count = 0
        resolution_s = 0.025  #[S]
        pulse_speed_difference = max_pulse_speed - ini_pulse_speed
        pulse_acceleration = pulse_speed_difference / acceleration_time
        unit_time_pulse_acceleration = int(pulse_acceleration * resolution_s)
        pulse_speed = ini_pulse_speed
        time_count = 0
        acceleration_num = int(acceleration_time / resolution_s)

        for i in range(acceleration_num):
            if self.emergency == True:
                return -1
            pulse_speed += unit_time_pulse_acceleration
            pulse_distance = int(pulse_speed * resolution_s)
            self.output_pulse_p(pulse_distance, pulse_speed)
            print(pulse_distance, pulse_speed)
            pulse_count += pulse_distance

        max_speed_pulse_distance = pulse_num-(pulse_count*2)
        if self.emergency == True:
            return -1
        self.output_pulse_p(max_speed_pulse_distance, pulse_speed)
        print(max_speed_pulse_distance, pulse_speed)
        pulse_count += max_speed_pulse_distance

        for i in range(acceleration_num):
            if self.emergency == True:
                return -1
            pulse_distance = int(pulse_speed * resolution_s)
            pulse_speed -= unit_time_pulse_acceleration
            self.output_pulse_p(pulse_distance, pulse_speed)
            print(pulse_distance, pulse_speed)
            pulse_count += pulse_distance

        print("pulse_distance =", pulse_count)

        return 0

    def trapezoid_pulse_rev(self, rotation, ini_rev_speed, max_rev_speed, acceleration_time):
    
        pulse_distance = int(self.rev_to_pulse(rotation))
        ini_pulse_speed = int(self.rev_to_pulse(ini_rev_speed))
        max_pulse_speed = int(self.rev_to_pulse(max_rev_speed))
        
        self.trapezoid_pulse_p(pulse_distance, ini_pulse_speed, max_pulse_speed, acceleration_time)

    def rev_to_pulse(self, rev):
        pulse = self.Rotational_pulse * rev
        return pulse

# micro step 2 のMAX
pulse_distance = 6000
ini_pulse_speed = 300
max_pulse_speed = 4500
acceleration_time = 0.5

rev_distance = 15
ini_rev_speed = 0.75
max_rev_speed = 11.25

if __name__ == '__main__':

    try:

        smotor = TB6600(enable_pin=4)
        smotor.init()

        while True:

            smotor.def_direction("CW")
            print("CW")
            # smotor.trapezoid_pulse_p(pulse_distance, ini_pulse_speed, max_pulse_speed, acceleration_time)
            smotor.trapezoid_pulse_rev(rev_distance, ini_rev_speed, max_rev_speed, acceleration_time)

            sleep(1)

            smotor.def_direction("CCW")
            print("CCW")
            # smotor.trapezoid_pulse_p(pulse_distance, ini_pulse_speed, max_pulse_speed, acceleration_time)
            smotor.trapezoid_pulse_rev(rev_distance, ini_rev_speed, max_rev_speed, acceleration_time)

            sleep(2)

    except KeyboardInterrupt:
        pass

    smotor.end()
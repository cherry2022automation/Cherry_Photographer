import TB6600
import RPi.GPIO as GPIO
from time import sleep

class cherry_slider():

    lim_min_pin = 24
    lim_max_pin = 23

    limit_true = GPIO.HIGH
    limit_false = GPIO.LOW

    now_abs_distance = 0
    pitch = 5   # [mm]

    ini_rev_speed = 0.75
    max_rev_speed = 13
    acceleration_time = 0.5

    origin_now = False
    max_now = False

    def __init__(self, **option):
        self.lim_ini()
        self.smotor = TB6600.TB6600()
        self.smotor.init()

    def emergency_stop_min(self, INT_PIN):
        sleep(0.05)
        if self.origin_now == True:
            return
        if GPIO.input(self.lim_min_pin)==self.limit_true:
            print('!!!!!emergency_stop(lim_min)!!!!!')
            self.smotor.emergency = True
            self.now_abs_distance = 0

    def emergency_stop_max(self, INT_PIN):
        sleep(0.05)
        if self.max_now == True:
            return
        if GPIO.input(self.lim_max_pin)==self.limit_true:
            print('!!!!!emergency_stop(lim_max)!!!!!')
            self.smotor.emergency = True
            self.now_abs_distance = 300
    
    def end(self):
        self.smotor.enable(False)
        GPIO.cleanup()

    def lim_ini(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(self.lim_min_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(self.lim_max_pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.add_event_detect(self.lim_min_pin, GPIO.RISING, callback=self.emergency_stop_min, bouncetime=200)
        GPIO.add_event_detect(self.lim_max_pin, GPIO.RISING, callback=self.emergency_stop_max, bouncetime=200)

    def origin(self):
        self.origin_now = True
        self.smotor.emergency = False
        self.smotor.enable(True)
        self.smotor.def_direction("CCW")
        while(GPIO.input(self.lim_min_pin)==self.limit_false):
            self.smotor.output_one_pulse(0.0005)
        self.now_abs_distance = 0
        self.smotor.emergency = False
        self.smotor.enable(False)
        sleep(0.5)
        self.origin_now = False

    
    def max(self):
        self.max_now = True
        self.smotor.emergency = False
        self.smotor.enable(True)
        self.smotor.def_direction("CW")
        while(GPIO.input(self.lim_max_pin)==self.limit_false):
            self.smotor.output_one_pulse(0.0005)
        self.now_abs_distance = 270
        self.smotor.emergency = False
        self.smotor.enable(False)
        sleep(0.5)
        self.max_now = False

    def move_abs(self, target_distance):
        move_distance = target_distance - self.now_abs_distance
        self.move_inc(move_distance)

    def move_inc(self, move_distance):
        self.now_abs_distance = self.now_abs_distance + move_distance
        if self.now_abs_distance < 5:
            print('Please specify the distance in the range of 10 ~ 300mm')
        move_rev_distance = self.mm_to_rev(move_distance)
        if self.smotor.emergency == True:
            print("!!!!!Emergency stop now!!!!!")
            print("!!!!!Please return to the origin!!!!!")
            return -1
        if move_rev_distance > 0:
            self.smotor.def_direction("CW")
        else:
            self.smotor.def_direction("CCW")
        self.smotor.enable(True)
        self.smotor.trapezoid_pulse_rev(abs(move_rev_distance), self.ini_rev_speed, self.max_rev_speed, self.acceleration_time)
        self.smotor.enable(False)
        return

    def mm_to_rev(self, mm):
        rev = mm / self.pitch
        return rev

if __name__ == '__main__':

    print('init')
    slider = cherry_slider()

    slider.origin()

    try:

        while(True):
            distance = float(input('distance(0 or 10~300) :'))
            if distance == 0:
                slider.origin()
                print('move origin')
            else:
                slider.move_abs(distance)
                print('move ' + str(distance) + 'mm')

    except:
        pass

    slider.end()
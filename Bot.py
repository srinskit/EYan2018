from time import sleep

from picamera import PiCamera
from picamera.array import PiRGBArray
from picamera.exc import PiCameraValueError
import RPi.GPIO as GPIO
import numpy as np


class Motor:
    def __init__(self, pin_a, pin_b, pin_e):
        self.pin_a, self.pin_b, self.pin_e = pin_a, pin_b, pin_e
        GPIO.setup(self.pin_a, GPIO.OUT)
        GPIO.setup(self.pin_b, GPIO.OUT)
        GPIO.setup(self.pin_e, GPIO.OUT)
        self.pwm = GPIO.PWM(self.pin_e, 100)
        self.pwm.start(0)
        self.v = 0

    def move_forwards(self):
        GPIO.output(self.pin_a, GPIO.LOW)
        GPIO.output(self.pin_b, GPIO.HIGH)

    def move_backwards(self):
        GPIO.output(self.pin_a, GPIO.HIGH)
        GPIO.output(self.pin_b, GPIO.LOW)

    def set_velocity(self, v):
        if v < 0 and self.v >= 0:
            self.move_backwards()
        if v >= 0 and self.v < 0:
            self.move_forwards()
        self.pwm.ChangeDutyCycle(abs(v))
        self.v = v

    def cleanup(self):
        self.pwm.stop()
        GPIO.output(self.pin_e, GPIO.LOW)


RED_LED = 12
GREEN_LED = 16
BLUE_LED = 18

soft_run = False
SMALL_RES = (640, 480)
# GOOD_RES = (640, 480)
GOOD_RES = (1312, 976)


def attach():
    global left_motor, right_motor, camera, capture_iterator
    global res_x, res_y, gray_size

    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    left_motor = Motor(32, 35, 37)
    right_motor = Motor(36, 38, 40)
    GPIO.setup(BLUE_LED, GPIO.OUT)
    GPIO.setup(GREEN_LED, GPIO.OUT)
    GPIO.setup(RED_LED, GPIO.OUT)
    GPIO.output(BLUE_LED, GPIO.LOW)
    GPIO.output(GREEN_LED, GPIO.LOW)
    GPIO.output(RED_LED, GPIO.LOW)

    camera = PiCamera(resolution=SMALL_RES)
    res_x, res_y = camera.resolution
    gray_size = res_y * res_x
    # camera.framerate = 5
    raw_capture = np.zeros(res_x * res_y * 3 / 2, dtype=np.uint8)
    capture_iterator = camera.capture_continuous(raw_capture, format='raw', use_video_port=True)


def get_view():
    try:
        gray = capture_iterator.next()
        return np.reshape(gray[:gray_size], (res_y, res_x))
    except (StopIteration, PiCameraValueError) as _:
        return None


def get_good_view():
    view = PiRGBArray(camera, GOOD_RES)
    camera.resolution = GOOD_RES
    camera.capture(view, format='bgr')
    camera.resolution = SMALL_RES
    return view.array


def move(left_v, right_v):
    print left_v, right_v
    if not soft_run:
        left_motor.set_velocity(left_v)
        right_motor.set_velocity(right_v)


def blink(color, n=1):
    pin = None
    n = min(n, 4)
    if color == 'Blue':
        pin = BLUE_LED
    elif color == 'Green':
        pin = GREEN_LED
    elif color == 'Red':
        pin = RED_LED
    for _ in range(n):
        GPIO.output(pin, GPIO.HIGH)
        sleep(1)
        GPIO.output(pin, GPIO.LOW)
        sleep(1)


def detach():
    left_motor.cleanup()
    right_motor.cleanup()
    GPIO.cleanup()
    camera.close()

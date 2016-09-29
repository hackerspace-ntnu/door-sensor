import threading
import time

import RPi.GPIO as GPIO

SENSOR_PIN = 4
LED_PINS = R_PIN, G_PIN, B_PIN = 22, 27, 17
BLINK_TIMEOUT = 0.25
COLORS = OFF, RED, GREEN, BLUE = (0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1)


def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PINS, GPIO.OUT)


def check_door():
    status = GPIO.input(SENSOR_PIN)
    return bool(status)


def set_led(red=0, green=0, blue=0):
    GPIO.output(R_PIN, red)
    GPIO.output(G_PIN, green)
    GPIO.output(B_PIN, blue)


class LEDControl:
    color = OFF

    def __init__(self):
        self.off()
        self.blinking = threading.Event()
        self.terminated = threading.Event()
        self.t = threading.Thread(target=self.__blink)
        self.t.start()

    def on(self):
        set_led(*self.color)

    def off(self):
        set_led(*OFF)

    def wait(self, seconds):
        time.sleep(seconds)

    def hold(self, color):
        self.color = color
        self.blinking.clear()

    def blink(self, color):
        self.color = color
        self.blinking.set()

    def __blink(self):
        while not self.terminated.is_set():
            if self.blinking.is_set():
                self.on()
                self.wait(BLINK_TIMEOUT)
                self.off()
                self.wait(BLINK_TIMEOUT)
            else:
                self.on()
                self.wait(BLINK_TIMEOUT)

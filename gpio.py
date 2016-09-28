import time

import RPi.GPIO as GPIO

SENSOR_PIN = 4
LED_PINS = R_PIN, G_PIN, B_PIN = 22, 27, 17
BLINK_PAUSE = 0.25


def check_door():
    status = GPIO.input(SENSOR_PIN)
    return bool(status)


# Initializes the GPIO pins on the raspberry pi
def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(LED_PINS, GPIO.OUT)

    blink_led(1, 1, 1, times=3)


def hold_led(red=0, green=0, blue=0):
    GPIO.output(R_PIN, red)
    GPIO.output(G_PIN, green)
    GPIO.output(B_PIN, blue)


def blink_led(red=0, green=0, blue=0, times=1):
    for _ in range(times):
        hold_led(0, 0, 0)
        time.sleep(BLINK_PAUSE)
        hold_led(red, green, blue)
        time.sleep(BLINK_PAUSE)

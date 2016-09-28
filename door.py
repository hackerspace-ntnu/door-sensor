import json
import logging
import sys
import requests
import time
from urllib.parse import urljoin
import RPi.GPIO as GPIO

#Settings
RECONNECT_DELAY = 60.0
MAX_TRIES = 5
TIMEOUT = 5.0
API_HOST = 'https://hackerspace-ntnu.no'
API_ENDPOINT = '/door/'
API_KEY = None #Intentionally set to None

SENSOR_PIN = 4
LED_PINS = R_PIN, G_PIN, B_PIN = 22, 27, 17
BLINK_PAUSE = 0.25

OPEN, CLOSED = True, False


#Logging
logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


#Gets api_key from file "KEY.txt"
def get_api_key():
    with open('KEY.txt', 'r') as open_file:
        return open_file.readline().strip()


#Checks status of door(boolean)
def check_door():
    status = GPIO.input(SENSOR_PIN)
    return bool(status)


#Post the status of door to url API_HOST+API_ENDPOINT
def post_status(status):
    data = {
        'key': API_KEY,
        'status': status,
    }
    url = urljoin(API_HOST, API_ENDPOINT)
    logging.info('Posting status {st} to {url}'.format(st=status, url=url))
    return requests.post(url, data=json.dumps(data))


#Initializes the GPIO pins on the raspberry pi
def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(SENSOR_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
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


#Main function that starts the program and calls post_status if state of door changes
if __name__ == '__main__':
    init_gpio()
    API_KEY = get_api_key()
    current_status = None

    logging.info('Starting door-watching busy loop')
    try:
        while True:
            current_status, old_status = check_door(), current_status
            tries = 0

            if current_status != old_status:
                while True:
                    hold_led(red=1, green=1)

                    try:
                        r = post_status(current_status)

                        if r.status_code == 200 or r.status_code == 201:
                            logging.info('Successfully posted status {} to API'.format(current_status))

                            if current_status == OPEN:
                                blink_led(green=1, times=3)
                            else:
                                blink_led(red=1, times=3)

                            break
                        else:
                            logging.warning('Server responded with status code {}'.format(r.status_code))
                            tries += 1

                    except requests.exceptions.ConnectionError:
                        logging.warning('ConnectionError')

                        if tries >= MAX_TRIES:
                            logging.warning('Stop trying to post status {status} after {tries} retries'.format(status=current_status, tries=tries))
                            break
                        else:
                            tries += 1

                    logging.warning('Failed to post status {status}, retrying in {delay}'.format(status=current_status, delay=RECONNECT_DELAY))
                    time.sleep(RECONNECT_DELAY)

            time.sleep(TIMEOUT)
    except KeyboardInterrupt:
        hold_led(0, 0, 0)
        logging.info('Loop interrupted by keyboard')
        exit(0)


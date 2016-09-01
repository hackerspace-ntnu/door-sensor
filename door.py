import json
import logging
import sys
import requests
import time
from urllib.parse import urljoin
import RPi.GPIO as GPIO

#Settings
RECONNECT_DELAY = 60.0
TIMEOUT = 5.0
API_HOST = 'https://hackerspace-ntnu.no'
API_ENDPOINT = '/door/'
GPIO_PIN = 18
API_KEY = None #Intentionally set to None

#Logging
logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)

#Gets api_key from file "KEY.txt"
def get_api_key():
    with open('KEY.txt', 'r') as open_file:
        return open_file.readline().strip()

#Checks status of door(boolean)
def check_door():
    status = GPIO.input(GPIO_PIN)
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
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

#Main function that starts the program and calls post_status if state of door changes
if __name__ == '__main__':
    init_gpio()
    API_KEY = get_api_key()
    current_status = False

    logging.info('Starting door-watching busy loop')
    while True:
        current_status, old_status = check_door(), current_status
        if current_status != old_status:
            r = post_status(current_status)
            while(r.status_code != 200):
                r = post_status(current_status)
                time.sleep(RECONNECT_DELAY)
        time.sleep(TIMEOUT)

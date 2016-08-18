import json
import logging
import sys
import time
from urllib.parse import urljoin

import RPi.GPIO as GPIO

import requests

TIMEOUT = 5.0 #seconds
API_HOST = 'https://hackerspace-ntnu.no'
API_ENDPOINT = '/door/'
GPIO_PIN = 18
API_KEY = None

logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


def get_api_key():
    with open('KEY.txt', 'r') as open_file:
        return open_file.readline().strip()

def check_door():
    status = GPIO.input(GPIO_PIN)
    return bool(status)

def post_status(status):
    data = {
        'key': API_KEY,
        'status': status,
    }
    url = urljoin(API_HOST, API_ENDPOINT)
    logging.info('Posting status {st} to {url}'.format(st=status, url=url))
    return requests.post(url, data=json.dumps(data))

def init_gpio():
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)

if __name__ == '__main__':
    init_gpio()
    API_KEY = get_api_key()
    current_status = False
    
    logging.info('Starting door-watching busy loop')
    while True:
        current_status, old_status = check_door(), current_status

        if current_status != old_status:
            post_status(current_status)

        time.sleep(TIMEOUT)

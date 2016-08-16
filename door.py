import RPi.GPIO as GPIO
import requests
import json
import time

TIMEOUT = 5.0 #seconds
API_HOST = 'https://hackerspace-ntnu.no'
API_ENDPOINT = '/api/door'
GPIO_PIN = 7
API_KEY = None

def get_api_key():
    with open('KEY.txt', 'r') as open_file:
       return open_file.readline().strip()

def check_door():
    status = GPIO.input(GPIO_PIN))
    return bool(status)

def post_status(status):
    data = {
        'key': API_KEY,
        'status': status
    }
    return requests.post(API_HOST + API_ENDPOINT, data=json.dumps(data))


if __name__ == '__main__':
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIOGPIO.PUD_DOWN)
    
    API_KEY = get_api_key()
    current_status = False	
    
    while True:
        current_status, old_status = check_door(), current_status

        if current_status != old_status:
            post_status(current_status)

        time.sleep(TIMEOUT)


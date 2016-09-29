import json
import logging
import sys
import time
from urllib.parse import urljoin

import requests

from gpio import BLUE, GREEN, RED, LEDControl, check_door, init_gpio

RECONNECT_DELAY = 60.0
MAX_TRIES = 5
TIMEOUT = 5.0
API_HOST = 'https://hackerspace-ntnu.no'
API_ENDPOINT = '/door/'
API_KEY = None  # Intentionally set to None

OPEN, CLOSED = True, False

# Logging
logging.basicConfig(format='%(asctime)s %(message)s', stream=sys.stdout, level=logging.INFO)


# Gets api_key from file "KEY.txt"
def get_api_key():
    with open('KEY.txt', 'r') as open_file:
        return open_file.readline().strip()


# Post the status of door to url API_HOST+API_ENDPOINT
def post_status(status):
    data = {
        'key': API_KEY,
        'status': status,
    }
    url = urljoin(API_HOST, API_ENDPOINT)
    logging.info('Posting status {st} to {url}'.format(st=status, url=url))
    return requests.post(url, data=json.dumps(data))


# Main function that starts the program and calls post_status if state of door changes
if __name__ == '__main__':
    init_gpio()
    LED = LEDControl()
    LED.blink(BLUE)

    API_KEY = get_api_key()
    current_status = None

    logging.info('Starting door-watching busy loop')
    try:
        while True:
            current_status, old_status = check_door(), current_status
            tries = 0

            if current_status != old_status:
                while True:
                    LED.hold(BLUE)

                    try:
                        r = post_status(current_status)

                        if r.status_code == 200 or r.status_code == 201:
                            logging.info('Successfully posted status {} to API'.format(current_status))

                            if current_status == OPEN:
                                LED.hold(GREEN)
                            else:
                                LED.hold(RED)

                            break
                        else:
                            LED.blink(BLUE)
                            logging.warning('Server responded with status code {}'.format(r.status_code))
                            tries += 1

                    except requests.exceptions.ConnectionError:
                        LED.blink(BLUE)
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
        LED.off()
        LED.terminated.set()
        logging.info('Loop interrupted by keyboard')
        exit(0)

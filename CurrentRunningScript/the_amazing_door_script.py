import RPi.GPIO as GPIO
import datetime
import time
import os
import httplib
import requests
import json


url = 'https://hackerspace-ntnu.no/door/'
GPIO_PIN = 4

#change timezone to Oslo
os.environ['TZ'] = 'Europe/Oslo'
time.tzset()

timeStart = "H:M:S"
dateStart = datetime.date.today() #todays date in fromat yyyy-mm-dd
canIComeIn = True
gpioOld = -7
minTimeLimit = 60

def calculate(dateStart, timeStart, dateEnd, timeEnd, timeTotal):
  #calculate, post all data to server and print test values

  dateEnd = dateEnd.strftime('%Y-%m-%d')
  timeEnd = timeEnd.strftime('%H:%M:%S')

  data = {'key':'hackerspace<3', 'status':0, 'dateStart':dateStart, 'timeStart':timeStart, 'dateEnd':dateEnd, 'timeEnd':timeEnd, 'timeTotal':timeTotal}

  try:
        r = requests.post(url, data = json.dumps(data))
  except requests.exceptions.RequestException as e:
        print e

  #uncomment test code below
  #print("Hackerspace var Apen " + dateStart + " kl " + timeStart + " og stengte " + dateEnd + " kl " + timeEnd + ".\nApent i " + str(timeTotal) + " sekunder.")


def avgTimeOpen(start, end):

        startSec = (start.hour * 3600) + (start.minute * 60) + start.second
        endSec = (end.hour * 3600) + (end.minute * 60) + end.second

        return endSec - startSec


def isOpen(input_state):
        return 1 if input_state == 1 else 0
        #this is a conditional expression... for the n00bs


def check_door(input_state):

        global canIComeIn, gpioOld, dateStart, timeStart, minTimeLimit, url

        gpio = input_state
        #canIComeIn is False if door never has been opened
        # State has changed, create connection to API.
        if(gpio != gpioOld):
            gpioOld = gpio


            if(isOpen(input_state)):
                #print("OPEN: " + str(input_state))

                counter = 0
                if(canIComeIn):
                        #canIComeIn er True forste gang script starter og blir satt til True naar dora lukkes
                        #put inn i while-lokka ->>> GPIO.input(GPIO_PIN) nede
                #only post timeStart and dateStart if and only if the door has been open >= 60 sec
                        while(counter < minTimeLimit and GPIO.input(GPIO_PIN)):
                                #print counter
                                time.sleep(1)
                                counter += 1

                        if(counter >= minTimeLimit):
                                timeStart = datetime.datetime.now().time()
                                dateStart = datetime.date.today()
                                canIComeIn = False

                                dateStart = dateStart.strftime('%Y-%m-%d')
                                timeStart = timeStart.strftime('%H:%M:%S')

                                #post json data to server

                                data = {'key':'hackerspace<3', 'status':input_state, 'timeStart':timeStart, 'dateStart':dateStart}
                                r = requests.post(url, data = json.dumps(data))
                                #print("STATUS FROM SERVER - OPEN: " + str(r.status_code))
            else:

                #print "CLOSED: " + str(input_state)
                data = {'key':'hackerspace<3', 'status':input_state}
                r = requests.post(url, data = json.dumps(data))
                #print("STATUS CODE FROM SERVER - CLOSE: " + str(r.status_code))
                if( not canIComeIn):
                        timeEnd = datetime.datetime.now().time()
                        dateEnd = datetime.date.today()
                        timeTotal = avgTimeOpen(datetime.datetime.strptime(timeStart, '%H:%M:%S'), timeEnd)

                        if(timeTotal > minTimeLimit):
                                calculate(dateStart, timeStart, dateEnd, timeEnd, timeTotal)

                #reset globals
                canIComeIn = True
                gpioOld = -7

if __name__ == '__main__':
 # Initialize the GPIO.
 GPIO.setmode(GPIO.BCM)
 GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_UP)
 #check status forever, only post when status change
 while True:
    check_door(GPIO.input(GPIO_PIN))

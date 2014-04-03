from twisted.internet import task
from twisted.internet import reactor
import requests
import RPi.GPIO as GPIO

GPIO.setmode(GPIO.BOARD)
GPIO.setup(7, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

timeout = 30.0 #seconds
api = "http://hackerspace.idi.ntnu.no/api/door"

def check_door():
	door_state = GPIO.input(7)
	#if door closed
	if door_state == 1:
		requests.put(api)
		print "door closed"
	#else door open
	else: 
		requests.post(api)
		print "door open"

l = task.LoopingCall(check_door)
l.start(timeout) # start calls every n seconds
reactor.run()

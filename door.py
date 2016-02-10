import RPi.GPIO as GPIO
import httplib, datetime, time
import sqlite3

date = time.asctime( time.localtime( time.time() ) )
opened_sec = -1

TIMEOUT = 5.0 #seconds
API_HOST = "hackerspace-ntnu.no"
API_ENDPOINT = "/api/door"
GPIO_PIN = 7

# connect or create if not exists sqlite3 db
def connect(today, opened, closed, total):

  conn = sqlite3.connect('door_graph.db')
  c = conn.cursor()

  c.execute(''' CREATE TABLE IF NOT EXISTS graph (today date, opened int, closed int, total int) ''')
  c.execute(" INSERT INTO graph (today, opened, closed, total) VALUES (?, ?, ?, ?)", [today, opened, closed, total] )

  #save
  conn.commit()

  conn.close()

def calculate(date, opened, closed):

  time = closed - opened
  if(time >= 30 and time <= 600000):
    print str(date) + " - Hackerspace has been open in " + str(time) + " seconds."
    connect(date, opened, closed, time)

def check_door(state):
  # Read state from GPIO.
  gpio = GPIO.input(GPIO_PIN)

  if state != gpio:
    # State has changed, create connection to API.
    conn = httplib.HTTPSConnection(API_HOST)

    if gpio == 1:
      conn.request('POST', API_ENDPOINT+"/closed")
      closed_sec = int(round(time.time()))
      global date, opened_sec
      calculate(date, opened_sec, closed_sec)
      print "Door closed"
    else:
      conn.request('POST', API_ENDPOINT+"/open")
      opened_sec = int(round(time.time())) 
      print "Door open"
  return gpio

if __name__ == '__main__':
  # Initialize the GPIO.
  GPIO.setmode(GPIO.BOARD)
  GPIO.setup(GPIO_PIN, GPIO.IN, pull_up_down = GPIO.PUD_DOWN)

  # Initialize state to 0.
  state = 0

  while True:
    # Sleep between checks, and run forever.
    state = check_door(state)
    time.sleep(TIMEOUT)

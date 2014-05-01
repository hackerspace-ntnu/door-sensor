# hackerspace-door

A client for the Hackerspace NTNU door RPi.

Simple program for reporting the status of the hackerspace door to the API at
http://hackerspace.idi.ntnu.no/api/door.

Reports are sent in the form of POST and PUT requests. PUT says the door is
closed, and POST that the door has opened.

## Installing dependencies.

You only need [RPi.GPIO](https://pypi.python.org/pypi/RPi.GPIO) which can be
installed with pip either as a system-package or in your virtual environment:

    $ virtualenv --system-site-packages venv
    $ source venv/bin/activate
    $ pip install -r requirements.txt

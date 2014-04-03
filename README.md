hackerspace-door
================

A client for the door pi.

Simple program for reporting the status of the hackerspace door to the API at http://hackerspace.idi.ntnu.no/api/door.
Reports are sent in the form of POST and PUT requests. Reports are sent periodically using the twisted framework.

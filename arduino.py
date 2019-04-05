import os

import serial

# find arduino tty
arduino_path = '/dev/'
arduino_tty = False
for file in os.listdir(arduino_path):
    if file.startswith('tty.usb'):
        arduino_tty = arduino_path + file
        break

# connect to arduino output
ser = serial.Serial(arduino_tty, 9600) if arduino_tty else None
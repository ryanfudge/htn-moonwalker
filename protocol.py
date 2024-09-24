#!/usr/bin/env python3

import time
import serial
import pyvesc
import RPi.GPIO as GPIO

SPEED = 10000
STOP = 0

DIV_CONST = 15
SLEEP_TIME = 0.0001

GO = True

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BOARD)

GPIO.setup(11, GPIO.OUT)
right_brake = GPIO.PWM(11,50)

GPIO.setup(12, GPIO.OUT)
left_brake = GPIO.PWM(12,50)

right_brake.start(0)
left_brake.start(0)

turn_right = False
turn_left = False

# Create a serial object to send serial messages
ser = serial.Serial(
    port='/dev/ttyS0',
    baudrate = 115200,
    parity=serial.PARITY_NONE,
    stopbits=serial.STOPBITS_ONE,
    bytesize=serial.EIGHTBITS,
    timeout=1
)

# Function to simplify the serial output for changing duty cycles
def changeDuty(num):
    ser.write(pyvesc.encode(pyvesc.SetDutyCycle(num)))
    time.sleep(SLEEP_TIME)

# Motor Control
while True:
    # Brake
    if not GO:
        changeDuty(0)
        break

    # Move
    if GO:
        changeDuty(10000)
        time.sleep(5)
        GO = False

    if turn_right:
        angle = 0
        right_brake.ChangeDutyCycle(2 + (angle / 18))
    elif turn_left:
        angle = 180
        left_brake.ChangeDutyCycle(2 + (angle / 18))
    else:
        angle = 90
        right_brake.ChangeDutyCycle(2 + (angle / 18))
        left_brake.ChangeDutyCycle(2 + (angle / 18))

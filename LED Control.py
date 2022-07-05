# SPDX-FileCopyrightText: 2018 Kattni Rembor for Adafruit Industries
#
# SPDX-License-Identifier: MIT

"""CircuitPython Essentials: PWM with Fixed Frequency example."""
import time
import board
import pwmio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

pwm = pwmio.PWMOut(board.D0, frequency=5000, duty_cycle=0)  # output on LED pin with default of 500Hz

pin1 = DigitalInOut(board.D2)
pin1.direction = Direction.INPUT
pin1.pull = Pull.UP

pin2 = DigitalInOut(board.D3)
pin2.direction = Direction.INPUT
pin2.pull = Pull.UP

switch1 = Debouncer(pin1)
switch2 = Debouncer(pin2)

step = 25
brightness = 25

while True:
    pwm.duty_cycle = int(brightness / 100 * 65535)

    switch1.update()
    if switch1.fell:
        if brightness != 100:
            brightness = brightness+step
            print("brightness increased to ", brightness)
        elif brightness == 100:
            print("reached max brightness: (", brightness, ")")

    switch2.update()
    if switch2.fell:
        if brightness != 0:
            brightness = brightness-step
            print("brightness decreased to ", brightness)
        elif brightness == 0:
            print("reached min brightness: (", brightness, ")")


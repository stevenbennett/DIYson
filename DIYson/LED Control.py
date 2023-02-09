import time
import board
import pwmio
import touchio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

pwm = pwmio.PWMOut(board.RX, frequency=1000, duty_cycle=0)

# increase brightness
pin1 = board.TX
switch1 = touchio.TouchIn(pin1)
switch1_debounced = Debouncer(switch1)

# decrease brightness
pin2 = board.D3
switch2 = touchio.TouchIn(pin2)
switch2_debounced = Debouncer(switch2)

# toggle power
pin3 = board.A1
powerSwitch = touchio.TouchIn(pin3)
powerSwitch_debounced = Debouncer(powerSwitch)

power = False
step = 25
brightness = 25


def fadeBetween(start, end, direction):
    distance = abs(start - end)
    increment = distance / step
    for cycle in range(start, end, direction):
        pwm.duty_cycle = int(cycle / 100 * 65535)
        time.sleep(.25 / increment)


while True:

    powerSwitch_debounced.update()
    if powerSwitch_debounced.rose:
        fadeBetween(0, brightness, 1)
        power = True

    while power:
        pwm.duty_cycle = int(brightness / 100 * 65535)

        powerSwitch_debounced.update()
        if powerSwitch_debounced.rose:
            fadeBetween(brightness, 0, -1)
            power = False

        switch1_debounced.update()
        if switch1_debounced.rose:
            if brightness != 100:
                fadeBetween(brightness, (brightness + step), 1)
                brightness = brightness + step

        switch2_debounced.update()
        if switch2_debounced.rose:
            if brightness != step:
                fadeBetween(brightness, (brightness - step), -1)
                brightness = brightness - step

    time.sleep(0.01)

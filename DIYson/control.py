from solarcycle import Solar as solar
from solarcycle import Hardware as hw

import time
import board
import pwmio
import touchio
from digitalio import DigitalInOut, Direction, Pull
from adafruit_debouncer import Debouncer

##PINS##
# increase brightness
hw.pin1 = board.TX
switch1 = touchio.TouchIn(hw.pin2)
switch1_debounced = Debouncer(switch1)

# decrease brightness
hw.pin2 = board.D3
switch2 = touchio.TouchIn(hw.pin2)
switch2_debounced = Debouncer(switch2)

# toggle power
hw.pin3 = board.A1
powerSwitch = touchio.TouchIn(hw.pin2)
powerSwitch_debounced = Debouncer(powerSwitch)

hw.pwm = pwmio.PWMOut(board.RX, frequency=1000, duty_cycle=0)
##device settings##
hw.power = False
hw.step = 25
hw.brightness = 25

hw.Tof = 'VL53L1X' #time of flight sensor 
hw.ALs = 'LTR-559' #ambient light sensor
hw.prx = 'LTR-559' #proximity sensor

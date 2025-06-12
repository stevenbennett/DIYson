import microcontroller
import watchdog
import time, board, busio, math
import digitalio
import adafruit_veml7700
from analogio import AnalogIn, AnalogOut
from touchio import TouchIn
from adafruit_debouncer import Debouncer
from barbudor_tmp75 import TMP75

##################
# INITIALIZATION #
##################
DEFAULT_MAX_16_BIT_VALUE = 65535 # this is currently equal to 0% brightness. I need to make sure this variable name makes sense and is used consistently.
max_16_bit_value = DEFAULT_MAX_16_BIT_VALUE
DEFAULT_POWER_OUTPUT = 90 # out of 100. used for global max power ceiling
POWER_OUTPUT_LIMIT = DEFAULT_POWER_OUTPUT  # used to adjust max output based on temperature
DAC_BRIGHTNESS_FLOOR = 50000 # use this to ensure low brightness settings are visible/optimal. also allows you to manual adjust the brightness of the lowest brightness level.
DAC_OFF_VALUE = DEFAULT_MAX_16_BIT_VALUE
BRIGHTNESS_RANGE = DAC_OFF_VALUE - DAC_BRIGHTNESS_FLOOR

# INITIALIZE THE RX PIN WHICH WILL TURN OFF THE IC SWITCH AFTER BOOT
switch_control = digitalio.DigitalInOut(board.RX)
switch_control.direction = digitalio.Direction.OUTPUT
switch_control.value = False

# INITIALIZE THE DAC OUT TO CONTROL THE LED DRIVER
dac_out = AnalogOut(board.A1)
# SET THE LED DRIVER OUTPUT OFF
dac_out.value = DAC_OFF_VALUE

# could add a delay here to make sure DAC is initialized before handing over control

# TURN THE IC SWITCH OFF, TURNING CONTROL OVER TO THE QTPY
switch_control.value = True

microcontroller.watchdog.timeout = 2
microcontroller.watchdog.mode = watchdog.WatchDogMode.RESET


# INITIALIZE SENSORS
# LIGHT SENSOR (VEML7700)
i2c = busio.I2C(board.SCL, board.SDA)
light_sensor = adafruit_veml7700.VEML7700(i2c)
light_sensor.integration_time = 100  

# temperature sensor(TMP75)
temp_sensor = TMP75(i2c)

# BUTTONS
power_button_raw = TouchIn(board.A2)
increase_button_raw = TouchIn(board.TX)
decrease_button_raw = TouchIn(board.A3)
power_button = Debouncer(lambda: power_button_raw.value)
increase_button = Debouncer(lambda: increase_button_raw.value)
decrease_button = Debouncer(lambda: decrease_button_raw.value)


############
# SETTINGS #
############
# LAMP SETUP
_power = False  # False means lamp is off by default (don't change)
auto_brightness = False
temperature_scaling = True # Setting this false disables brightness scaling when temp sensor hits HIGH_TEMP. for safety the lamp will always turn off and stay off when it reaches MAX_TEMP
temperature_sample_rate = 5 #time in seconds to poll temperature sensor, not much benefit to reducing this (outside of testing)

# LED BRIGHTNESS CONFIG
# should probably update this so you can just declare one variable like `brightnesslevels = 4` and STEP, MIN_BRIGHTNESS, and MAX_BRIGHTNESS are calculated from that. This would allow you to easily go from 3 to 4 to 5 or even like 10 brightness levels without having to change a bunch of other variables. It might also break something even if you did all of that.
BRIGHTNESS_LEVELS = 4
STEP = 100 // BRIGHTNESS_LEVELS
MIN_BRIGHTNESS = STEP
MAX_BRIGHTNESS = STEP * (100 // STEP)
FADE_DURATION = 0.25
FADE_STEPS = 50
last_temp_check = 0

# AMBIENT LIGHT SENSOR CONFIG
LIGHT_SENSOR_MAX = 12000
LIGHT_SENSOR_MIN = 1

# TEMPERATURE SENSOR CONFIG
# these are conservative estimates based on PLA glass transition temperature of ~60c. can be bumped up a bit for PETG(75-80c) and bumped up quite a lot for polycarbonate 130c+ (check other component limits though...)
# internal temps can reach 56c if DEFAULT_POWER_OUTPUT is 100. haven't test at 90 or below.
HIGH_TEMP = 45
MAX_TEMP = 50

# CAPACITIVE TOUCH THRESHOLD, INCREASE IF TOO SENSITIVE
power_button_raw.threshold = 20000
increase_button_raw.threshold = 20000
decrease_button_raw.threshold = 20000


#############
# FUNCTIONS #
#############
# CLASSES
class Brightness:
    def __init__(self, percentage):
        self.flat_percentage = min(max(percentage, 0), 100)

    def as_driver_output(self):  # Converts from percentage to equivalent DAC output for the driver
        if self.flat_percentage == 0:
            return DAC_OFF_VALUE
        # Scale the brightness by the power output limit
        effective_percentage = (self.flat_percentage * POWER_OUTPUT_LIMIT) / 100
        normalized_brightness = effective_percentage / 100
        scaled_brightness = 1 - (normalized_brightness ** 2)
        dac_value = int(scaled_brightness * DAC_BRIGHTNESS_FLOOR)
        return dac_value

class AmbientBrightness:
    def __init__(self, sensor, min_value, max_value):
        self.sensor = sensor
        self.min_value = min_value
        self.max_value = max_value
        self.last_task_time = time.monotonic()

    def update(self): #limit frequency of value updates (hopefully allows lamp to wait for stable lighting conditions)
        if time.monotonic() - self.last_task_time >= 2:
            self.last_task_time = time.monotonic()
            return self.sensor.lux
        return None

    def get_brightness_lux(self):
        return self.sensor.lux


    def get_brightness_percentage(self): #converts the lux value to a scaled value then to a percentage to compare to user_brightness
        lux = self.sensor.lux
        shifted_lux = lux - self.min_value + 1  
        normalized_lux = shifted_lux / (self.max_value - self.min_value + 1)
        scaled_brightness = (math.log(normalized_lux * 9 + 1) / math.log(10)) * 100

        return min(max(scaled_brightness, 0), 100)


# SET INITIAL BRIGHTNESS
user_brightness = Brightness(STEP)
output_brightness = Brightness(0)
ambient_brightness = AmbientBrightness(light_sensor, LIGHT_SENSOR_MIN, LIGHT_SENSOR_MAX)


def get_temperature():
    # debugging
    # print(f"Temperature: {temp_sensor.temperature_in_C}°C")

    return temp_sensor.temperature_in_C

def set_output_brightness(target_brightness, duration=FADE_DURATION):
    global output_brightness
    step_duration = duration / FADE_STEPS

    # manually set some end points if start or end value is "off" for smoother tranistions
    start_value = DAC_OFF_VALUE if output_brightness.flat_percentage == 0 else output_brightness.as_driver_output()
    end_value = DAC_OFF_VALUE if target_brightness.flat_percentage == 0 else target_brightness.as_driver_output()

    for step in range(FADE_STEPS + 1):
        fraction = step / FADE_STEPS
        current_value = int(start_value + (end_value - start_value) * fraction)
        dac_out.value = current_value
        time.sleep(step_duration)

    output_brightness = target_brightness

    # debugging
    # print(f"Current brightness: {output_brightness.flat_percentage}% | DAC Output: {output_brightness.as_driver_output()}")

def handle_auto_brightness():
    global user_brightness
    ambient_percentage = ambient_brightness.get_brightness_percentage()
    new_brightness = user_brightness.flat_percentage  # start with current brightness

    # debugging
    # print(f"Comparing user brightness ({user_brightness.flat_percentage}) to ambient brightness ({ambient_brightness.get_brightness_percentage()}) at {ambient_brightness.sensor.lux}lux")

    if ambient_percentage >= new_brightness + STEP:
        new_brightness = min(new_brightness + STEP, MAX_BRIGHTNESS)
    elif ambient_percentage <= new_brightness - STEP:
        new_brightness = max(new_brightness - STEP, MIN_BRIGHTNESS)

    if new_brightness != user_brightness.flat_percentage:
        user_brightness = Brightness(new_brightness)
        set_output_brightness(user_brightness)

def handle_power_button():
    global _power, last_temp_check
    power_button.update()
    
    if power_button.rose:
        if _power:
            print("Turning off")
            set_output_brightness(Brightness(0))
            _power = False
        else:
            # if get_temperature() < MAX_TEMP:
            print("Turning on")
            set_output_brightness(user_brightness)
            last_temp_check = 0
            _power = True
            # else:
            #     print("Temperature too high to turn on the lamp")

def handle_increase_button():
    global user_brightness
    increase_button.update()

    if increase_button.rose:
        user_brightness = Brightness(min(user_brightness.flat_percentage + STEP, MAX_BRIGHTNESS))
        set_output_brightness(user_brightness)

def handle_decrease_button():
    global user_brightness
    decrease_button.update()

    if decrease_button.rose:
        user_brightness = Brightness(max(user_brightness.flat_percentage - STEP, MIN_BRIGHTNESS))
        set_output_brightness(user_brightness)

def check_temperature():
    global _power, POWER_OUTPUT_LIMIT, last_temp_check, user_brightness
    
    # Only check temperature every 2 seconds
    if time.monotonic() - last_temp_check < temperature_sample_rate:
        return
    last_temp_check = time.monotonic()

    temperature = get_temperature()

    # if temperature reaches or exceeds MAX_TEMP, turn the lamp off
    if temperature >= MAX_TEMP and _power:
        # debugging
        # print(f"Temperature {temperature: }C >= MAX_TEMP. Turning off lamp.")

        set_output_brightness(Brightness(0))
        _power = False
        return

    if temperature_scaling:
        # if temperature is high but below MAX_TEMP, start down-scaling the power output
        if temperature >= HIGH_TEMP:
            new_limit = int(DEFAULT_POWER_OUTPUT * (MAX_TEMP - temperature) / (MAX_TEMP - HIGH_TEMP))
            new_limit = max(0, min(new_limit, DEFAULT_POWER_OUTPUT))
            if new_limit != POWER_OUTPUT_LIMIT:
                print(f"Temperature {temperature: }C > HIGH_TEMP. Scaling power output limit to {new_limit}%")
                POWER_OUTPUT_LIMIT = new_limit
                set_output_brightness(user_brightness)
        
        # if temperature is below HIGH_TEMP - 2c, restore the default power limit
        elif temperature < (HIGH_TEMP - 2):
            if POWER_OUTPUT_LIMIT != DEFAULT_POWER_OUTPUT:
                print(f"Temperature {temperature: }C is below HIGH_TEMP({HIGH_TEMP}C). Restoring global power output limit to {DEFAULT_POWER_OUTPUT}%")
                POWER_OUTPUT_LIMIT = DEFAULT_POWER_OUTPUT
                set_output_brightness(user_brightness)

#############
# MAIN LOOP #
#############
def run():
    while True:
        microcontroller.watchdog.feed()
        handle_power_button()
        if _power:
            handle_increase_button()
            handle_decrease_button()
            if auto_brightness:
                handle_auto_brightness()
            check_temperature()
        time.sleep(0.01) #this is a good frequency for button presses, but really fast for sensor updates. add a higher limit when polling sensors (though i2c seems to ok polling really fast)
run()
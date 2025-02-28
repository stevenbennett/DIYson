import time, board
from analogio import AnalogIn, AnalogOut
from touchio import TouchIn
from adafruit_debouncer import Debouncer

# LED BRIGHTNESS CONFIG
DEFAULT_MAX_16_BIT_VALUE = 65535
STEP = 25
MIN_BRIGHTNESS = 25
MAX_BRIGHTNESS = 100
FADE_DURATION = 0.25
FADE_STEPS = 50

# AMBIENT LIGHT SENSOR CONFIG
LIGHT_SENSOR_MAX = 62000
LIGHT_SENSOR_MIN = 1000

# TEMPERATURE SENSOR CONFIG
HIGH_TEMP = 44
MAX_TEMP = 48
NUM_SAMPLES = 10

# VARIABLES
max_dac_output = 50000 # adjust based on desired minimum LED output
auto_brightness = False

# CLASSES
class Brightness:
    
    def __init__(self, percentage):
        self.flat_percentage = min(max(percentage, 0), 100)

    def as_driver_output(self):
        if self.flat_percentage == 0:
            return DEFAULT_MAX_16_BIT_VALUE
        normalized_brightness = self.flat_percentage / 100 
        scaled_brightness = 1 - (normalized_brightness ** 2)
        dac_value = int(scaled_brightness * max_dac_output)
        
        return dac_value

class AmbientBrightness:
    def __init__(self, light_sensor, min_value, max_value):
        self.light_sensor = light_sensor
        self.min_value, self.max_value = min_value, max_value
        self.last_task_time = time.monotonic()
    def get_weighted_ambient_brightness(self, x):
        x = min(max(x, self.min_value), self.max_value)
        return (x - self.min_value) * (MAX_BRIGHTNESS / (self.max_value - self.min_value))
    def update(self):
        if time.monotonic() - self.last_task_time >= 1:
            self.last_task_time = time.monotonic()
            return self.get_weighted_ambient_brightness(self.light_sensor.value)
        return None



# INITIALIZE PINS
dac_out = AnalogOut(board.A1)
light_sensor = AnalogIn(board.SCL)
temp_sensor = AnalogIn(board.RX)



# POWER STATE (OFF BY DEFAULT)
power = False
dac_out.value = DEFAULT_MAX_16_BIT_VALUE

# SET INITIAL BRIGHTNESS
user_brightness = Brightness(STEP)
output_brightness = Brightness(0)

# BUTTONS
power_button_raw = TouchIn(board.A2)
increase_button_raw = TouchIn(board.TX)
decrease_button_raw = TouchIn(board.A3)
power_button = Debouncer(lambda: power_button_raw.value)
increase_button = Debouncer(lambda: increase_button_raw.value)
decrease_button = Debouncer(lambda: decrease_button_raw.value)

# CAPACITIVE TOUCH THRESHOLD, INCREASE IF TOO SENSITIVE
power_button_raw.threshold = 20000
increase_button_raw.threshold = 20000
decrease_button_raw.threshold = 20000


def get_temperature():
    total = sum(temp_sensor.value for _ in range(NUM_SAMPLES))
    return (total * (3.3 / 65536) / NUM_SAMPLES) * 100 - 50

ambient_brightness = AmbientBrightness(light_sensor, LIGHT_SENSOR_MIN, LIGHT_SENSOR_MAX)

def set_output_brightness(target_brightness, duration=FADE_DURATION):
    global output_brightness
    step_duration = duration / FADE_STEPS

    for step in range(FADE_STEPS):
        intermediate_brightness = output_brightness.flat_percentage + (
            (target_brightness.flat_percentage - output_brightness.flat_percentage) * step / FADE_STEPS)
        
        dac_value = Brightness(intermediate_brightness).as_driver_output()

        if target_brightness.flat_percentage == 0:
            dac_value = int(dac_value + (DEFAULT_MAX_16_BIT_VALUE - dac_value) * (step / FADE_STEPS))

        dac_out.value = dac_value
        time.sleep(step_duration)

    output_brightness = target_brightness
    final_dac_value = DEFAULT_MAX_16_BIT_VALUE if output_brightness.flat_percentage == 0 else output_brightness.as_driver_output()
    dac_out.value = final_dac_value 

    # debugging
    # print(f"Current brightness: {output_brightness.flat_percentage}% | DAC Output: {final_dac_value}")

    if output_brightness.flat_percentage == 0:
        print(f"DEBUG: LED should be OFF | DAC Value: {final_dac_value}")

def handle_auto_brightness():
    global user_brightness
    ambient_level = ambient_brightness.update()
    if ambient_level:
        new_brightness = user_brightness.flat_percentage
        if ambient_level >= new_brightness + STEP:
            new_brightness = min(new_brightness + STEP, MAX_BRIGHTNESS)
        elif ambient_level <= new_brightness - STEP:
            new_brightness = max(new_brightness - STEP, MIN_BRIGHTNESS)

        if new_brightness != user_brightness.flat_percentage:
            user_brightness = Brightness(new_brightness)
            set_output_brightness(user_brightness)

def handle_power_button():
    global power
    power_button.update()
    
    if power_button.rose:
        if power:
            print("Turning off")
            set_output_brightness(Brightness(0))
            power = False
        else:
            if get_temperature() < MAX_TEMP:
                print("Turning on")
                set_output_brightness(user_brightness)
                power = True
            else:
                print("Temperature too high to turn on the lamp")

def handle_increase_button():
    global user_brightness
    increase_button.update()

    if increase_button.rose:
        print("Increasing brightness")
        user_brightness = Brightness(min(user_brightness.flat_percentage + STEP, MAX_BRIGHTNESS))
        set_output_brightness(user_brightness)

def handle_decrease_button():
    global user_brightness
    decrease_button.update()

    if decrease_button.rose:
        print("Decreasing brightness")
        user_brightness = Brightness(max(user_brightness.flat_percentage - STEP, MIN_BRIGHTNESS))
        set_output_brightness(user_brightness)

def check_temperature():
    global max_16_bit_value, power
    temperature = get_temperature()

    if temperature >= MAX_TEMP and power:
        print("Temperature exceeds max temp, turning off")
        set_output_brightness(Brightness(0))
        power = False
    elif temperature >= HIGH_TEMP:
        if max_16_bit_value == DEFAULT_MAX_16_BIT_VALUE:
            print("High temperature reached, reducing brightness")
            max_16_bit_value = int(DEFAULT_MAX_16_BIT_VALUE * 0.75)
        else:
            print("Still too hot")
    elif max_16_bit_value != DEFAULT_MAX_16_BIT_VALUE and temperature < (HIGH_TEMP - 2):
        print("Temperature below threshold, restoring brightness")
        max_16_bit_value = DEFAULT_MAX_16_BIT_VALUE

def run():
    while True:
        handle_power_button()
        if power:
            handle_increase_button()
            handle_decrease_button()
            if auto_brightness:
                handle_auto_brightness()
            # check_temperature()
        time.sleep(0.01)

run()
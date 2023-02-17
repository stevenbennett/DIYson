#write a class for the light
from datetime import datetime, timezone
import time
from suntime import Sun, SunTimeException #pip install suntime
import math
import json
from data.handle_data import Data
try: 
    import board
    import pwmio
    import touchio
    from digitalio import DigitalInOut, Direction, Pull
    from adafruit_debouncer import Debouncer
except:
    pass #for testing on PC

class Solar:
    def __init__(self):
        self.min_color_temp = 0
        self.max_color_temp = 10000
        self.latitude = 51.300705
        self.longitude = 0.421895

        self.min_cct = 0
        self.max_cct = 10000
        self.min_bri,self.max_bri = 0,100
        self.minlux,self.maxlux = 100,10000
        self.cri = 90

        self.wakeup_time = 7
    
    def utc_to_local(self,utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def date(self):
        now = datetime.now()
        current_date = now.strftime("%d/%m/%Y")
        return current_date
    def time(self):
        #calculate the time in milliseconds
        now = datetime.now()
        current_time = now.strftime("%H:%M:%S")
        hours = int(now.strftime("%H"))
        mins = int(now.strftime("%M"))
        secs = int(now.strftime("%S"))
        return hours,mins,secs
    
    def solar_insolation(self):
        # time = time in hours
        # date = datetime object
        # longitude = longitude in degrees
        # latitude = latitude in degrees

        # Define constants
        I_sc = 1367 # solar constant (W/m^2)
        β = 0.6 # atmospheric turbidity factor (unitless)
        d = 1.01 # earth-sun distance (astronomical units)

        h,m,s = self.time()
        time = h + m/60 + s/3600
        date = datetime.today()

        # Calculate solar declination
        day_of_year = date.timetuple().tm_yday
        solar_declination = 23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365)

        # Calculate solar hour angle
        solar_hour_angle = 15 * (time - 12)

        # Calculate solar zenith angle
        cos_zenith = math.sin(math.radians(self.latitude)) * math.sin(math.radians(solar_declination)) + \
                    math.cos(math.radians(self.latitude)) * math.cos(math.radians(solar_declination)) * \
                    math.cos(math.radians(solar_hour_angle))
        solar_zenith = math.degrees(math.acos(cos_zenith))

        # Calculate solar insolation
        I = I_sc * cos_zenith * (1 - β) / d**2

        brightness = min((max(0,I)/I_sc)*200,self.min_bri)
        if brightness < self.min_bri:
            brightness = self.min_bri
        elif brightness > self.max_bri:
            brightness = self.max_bri
        return brightness
    
    def sunrise_sunset(self):
        sun = Sun(self.latitude, self.longitude)
        #sunrise and sunset in UTC
        today_sr = self.utc_to_local(sun.get_sunrise_time())
        today_ss = self.utc_to_local(sun.get_sunset_time())
        hours_sr,mins_sr,secs_sr = int(today_sr.strftime("%H")), int(today_sr.strftime("%M")), int(today_sr.strftime("%S"))
        hours_ss,mins_ss,secs_ss = int(today_ss.strftime("%H")), int(today_ss.strftime("%M")), int(today_ss.strftime("%S"))
        print(today_sr,today_ss)
        return [hours_sr,mins_sr,secs_sr],[hours_ss,mins_ss,secs_ss]
    def calculate_parabola(self):
        #calculate the prabola of the CCT curve of the sun dependent on the time of day
        #this calculates the parabola when sunset/sunrise changes
        # x is equal to the time in milliseconds/1000 
        # y is the CCT of the LED

        #(a1,b1) (a2,b2) (a3,b3) are the points that lie on the parabola where a1 is the sunrise, a2 is midday and a2 is the sunset
        # sr/ss = [hours,mins,secs]
        sr,ss = self.sunrise_sunset()
        print(ss,sr)
        sr = sr[0]+(sr[1]/60)+(sr[2]/3600)
        ss = ss[0]+(ss[1]/60)+(ss[2]/3600)
        a1,a3 = sr,ss
        b1,b3 = 2000, 2000
        if self.min_cct > 2000:
            b1,b3 = self.min_cct, self.min_cct
        a2,b2 = 12000,6000
        print(a1,b1,a2,b2,a3,b3,ss,sr)
        hours,mins,secs = self.time()
        x = hours+(mins/60)+(secs/3600)
        c1 = b1*(((x-a2)*(x-a3))/((a1-a2)*(a1-a3)))
        c2 = b2*(((x-a1)*(x-a3))/((a2-a1)*(a2-a3)))
        c3 = b3*(((x-a1)*(x-a2))/((a3-a1)*(a3-a2)))
        cct = c1+c2+c3
        return cct
    
    def cct(self):
        cct = self.calculate_parabola()
        print(cct)
        if cct < self.min_color_temp:
            cct = self.min_color_temp
        elif cct > self.max_color_temp:
            cct = self.max_color_temp
        return(int(cct))
    
    def age_intensity_multiplier(self,age):
        return max(1,((1/382.5)*(min(age,100)**2))-1.4)
    
class Hardware:
    def __init__(self): ##### MADE FOR RASPI #####
        ##INFO##
        self.Tof = '' # VL53L1X time of flight sensor 
        self.ALs = '' # LTR-559 ambient light sensor
        self.prx = '' # LTR-559 proximity sensor

        ##VALUES##
        self.power = False
        self.step = 25
        self.brightness = 25
        self.dist_to_bri = [100,20]

        ##PINS##
        self.pwm = pwmio.PWMOut(board.RX, frequency=1000, duty_cycle=0)
        self.pin1 = board.TX
        self.pin2 = board.D3
        self.pin3 = board.A1
    def setup(self,i2cbus:list):
        if self.Tof == 'VL53L1X':
            import VL53L1X
            tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=i2cbus[0]) #defat i2c address: 0x29
            tof.open()
        if self.ALs == 'LTR-559':
            from ltr559 import LTR559
            ALs = LTR559()
            ALs.update_sensor()
        elif self.prx == 'VEML7700':
            import adafruit_veml7700 #pip3 install adafruit-circuitpython-veml7700import adafruit_veml7700
            i2c = board.I2C()  # uses board.SCL and board.SDA
            ALs = adafruit_veml7700.VEML7700(i2c)
        if self.prx == 'LTR-559':
            from ltr559 import LTR559
            prx = LTR559()
            prx.update_sensor()
        return tof,ALs,prx
    def check_values(self,value):
        if value < 0:
            value = 0
        elif value > 100:
            value = 100
        return value
    def set_cct(self,cct):
        pass #add code relevent to hardware

    def set_brightness(self,start, end, direction):
        distance = abs(start - end)
        increment = distance / self.step
        for cycle in range(start, end, direction):
            self.pwm.duty_cycle = int(cycle / 100 * 65535)
            time.sleep(.25 / increment)
        self.brightness = end

    def get_distance(self):
        #docs: https://github.com/pimoroni/vl53l1x-python
        if self.Tof == 'VL53L1X':
            import VL53L1X
            tof = VL53L1X.VL53L1X(i2c_bus=1, i2c_address=0x29)
            tof.open()
            tof.start_ranging(1)  # Start ranging
            # 0 = Unchanged
            # 1 = Short Range
            # 2 = Medium Range
            # 3 = Long Range
            distance_in_mm = tof.get_distance()
            tof.stop_ranging()  # Stop ranging
            return distance_in_mm
        else:
            return None
        
    def get_ambient_light(self):
        #Docs: https://github.com/pimoroni/ltr559-python
        if self.ALs == 'LTR-559':
            from ltr559 import LTR559
            ltr559 = LTR559()
            ltr559.update_sensor()
            lux = ltr559.get_lux()
            return lux
        elif self.ALs == 'VEML7700':
            ##code from adafruit website: https://learn.adafruit.com/adafruit-veml7700/python-circuitpython
            pass
        else:
            return None
        
    def get_proximity(self):
        if self.prx == 'LTR-559':
            from ltr559 import LTR559
            ltr559 = LTR559()
            ltr559.update_sensor()
            prox = ltr559.get_proximity()
            return prox
        else: 
            return None
        
    async def set_inside_brightness(self,type):
        if type == 'ambient':
            brightness = self.get_ambient_light()
            highest_brightness = Data.find(['brightness', 'high'])
            brightness = (((-1*(1/100)*brightness**2)+100)/highest_brightness)*100 #calculate the brightness in a percentage using the ambient light sensor
            return self.check_values(brightness)
        elif type == 'proximity':
            distance = self.get_distance()
            if distance != None:
                brightness = (self.dist_to_bri[0]/self.dist_to_bri[1])*distance
                return self.check_values(brightness)
        elif type == 'dual':
            ambient = self.set_inside_brightness('ambient')
            proximity = self.set_inside_brightness('proximity')
            brightness = (ambient+proximity)/2
            return self.check_values(brightness)
        elif type == 'tri':
            ambient = self.set_inside_brightness('ambient')
            proximity = self.set_inside_brightness('proximity')
            brightness = (ambient+proximity+self.brightness)/3
            return self.check_values(brightness)


light = Solar()
print(light.cct(),'cct')
print(light.solar_insolation(),'solar insolation')

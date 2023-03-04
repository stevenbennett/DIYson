"""
MIT License
Copyright (c) 2023 Joseph0M

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.
"""

from datetime import datetime, timezone
from suntime import Sun, SunTimeException #pip install suntime
import math

class Solar:
    def __init__(self):
        ##LOCATION##
        self.latitude = 51.4934
        self.longitude = 0.0098 #Exampe Values
        ##LED VALUES##
        self.LED_Values = {
            'CCT': {
                'min_CCT': 1800,
                'max_CCT': 6500, #(Kelvin) Defalt Values, Change to suit your LED's

                'sunrise_CCT': 2000,
                'noon_CCT': 6000, #Kelvin, Values for sun tracking
                'sunset_CCT': 2000,
            },

            'BRIGHTNESS': {
                'min_BRT': 0,
                'max_BRT': 100, #Percentage

                'min_lux': None,
                'max_lux': None, #Values in Lux (Lumens/centre desk area)
            },

            'CRI': 90
        }
    def get_LED_Values(self,value):
        table = self.LED_Values
        for type in table:
            if value in table[type]:
                return table[type][value]
        return None

    def utc_to_local(self,utc_dt):
        return utc_dt.replace(tzinfo=timezone.utc).astimezone(tz=None)

    def time(self):
        now = datetime.now()
        return int(now.strftime("%H")),int(now.strftime("%M")),int(now.strftime("%S"))
    
    def solar_insolation(self):
        I_sc = 1367 # solar constant (W/m^2)
        β = 0.6 # atmospheric turbidity factor (unitless)
        d = 1.01 # earth-sun distance (astronomical units)
        h,m,s = self.time()
        date = datetime.today()
        day_of_year = date.timetuple().tm_yday
        solar_declination = 23.45 * math.sin(2 * math.pi * (284 + day_of_year) / 365) # Calculate solar declination
        solar_hour_angle = 15 * ((h+m/60+s/3600) - 12) # Calculate solar hour angle
        cos_zenith = math.sin(math.radians(self.latitude)) * math.sin(math.radians(solar_declination)) + math.cos(math.radians(self.latitude)) * math.cos(math.radians(solar_declination)) * math.cos(math.radians(solar_hour_angle))
        solar_zenith = math.degrees(math.acos(cos_zenith)) # Calculate solar zenith angle

        I = I_sc * cos_zenith * (1 - β) / d**2
        brightness = min(self.get_LED_Values('max_BRT'),max(self.get_LED_Values('min_BRT'),max(0,I)/I_sc)*100)
        return brightness #Percentage
    
    def sunrise_sunset(self):
        sun = Sun(self.latitude, self.longitude)
        today_sr = self.utc_to_local(sun.get_sunrise_time())
        today_ss = self.utc_to_local(sun.get_sunset_time())
        return int(today_sr.strftime("%H"))+(int(today_sr.strftime("%M"))/60)+(int(today_sr.strftime("%S"))/3600), int(today_ss.strftime("%H"))+(int(today_ss.strftime("%M"))/60)+(int(today_ss.strftime("%S"))/3600)
    
    def cct(self):
        sr,ss = self.sunrise_sunset()
        print(sr,ss)
        a1,b1,a2,b2,a3,b3 = sr,min(self.get_LED_Values('max_CCT'),max(self.get_LED_Values('min_CCT'),self.get_LED_Values('sunrise_CCT'))),12,min(self.get_LED_Values('max_CCT'),max(self.get_LED_Values('min_CCT'),self.get_LED_Values('noon_CCT'))),ss,min(self.get_LED_Values('max_CCT'),max(self.get_LED_Values('min_CCT'),self.get_LED_Values('sunset_CCT')))
        hours,mins,secs = self.time()
        x = hours+(mins/60)+(secs/3600)
        cct = (b1*(((x-a2)*(x-a3))/((a1-a2)*(a1-a3))))+(b2*(((x-a1)*(x-a3))/((a2-a1)*(a2-a3))))+(b3*(((x-a1)*(x-a2))/((a3-a1)*(a3-a2))))
        return int(max(self.get_LED_Values('min_CCT'),min(cct,self.get_LED_Values('max_CCT'))))
    
    def age_intensity_multiplier(self,age):
        return max(1,((1/382.5)*(min(age,100)**2))-1.4) #multiply by the intensity to get the correct value (percentage)

def example_code():
    solar = Solar()
    print(f"Sunrise: {solar.sunrise_sunset()[0]}")
    print(f"Sunset: {solar.sunrise_sunset()[1]}")
    print(f"Time: {solar.time()[0]}:{solar.time()[1]}:{solar.time()[2]}")
    print(f"Sunlight Intensity: {solar.solar_insolation()}%")
    print(f"CCT: {solar.cct()}K")
    print(f"Age Intensity Multiplier: {solar.age_intensity_multiplier(50)}")
example_code()
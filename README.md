# DIYson
Components for making the DIYson lamp. Learn more on [Youtube](https://www.youtube.com/channel/UCvnxvXWYcOlmhRFvZ_ISP8g).

All designs are likely (probably guaranteed) to change. 3D models are updated regularly for education and experimentation, but will almost certainly be updated, replaced, or removed in the future.

# Fork Changes
This provides an early look at how an algorithm could be used in the main branch. The main class (Solar in solarcycle.py) replicates most of the features found in the official product including **locally Matching the CCT (Color Temperature) to the sun**, using sunrise and sunset to **calculate solar insolation (brightness) of the sun** and much more.
## Features:
* Matches CCT (Color Temperature) to the Sun
* Matches brightness of the sun (Solar Insolation)
* Distance/ambient light Dependant intensity
### Currently working on:
* Sunrise/Sunset warming
* Changes intensity dependent on Age
* Motion/Presence activated light
# Hardware
Hardware that is ideal/required are listed below:

* LED with tunable CCT
  * CCT range with 2000-6000k is ideal
  * Adjustable brightness
* VL53L1X Time of Flight sensor
  * Pimoroni version is great, but bulky
* LTR-559 Ambient Light Sensor
  * Again, Pimoroni version is great for development, but bulky
## Future additions to Hardware:
* PCB Intergrating sensors
* Dual PCB that splits main LED/microcontroller and sensors
* Architecture change from Adafruit QT Py to a RP2040 Board. eg Pimoroni PIM558

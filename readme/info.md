# Solar Tracking with the DIYson
The aim with this algorithm is to provide the capability of changing **CCT (Colour Temperature)** and **intensity** based on the sun's movement throughout the day. it also includes the age multiplyer function that **vearies the light intensity based on age**, replicating the feature from Dyson. Although the DIYson currently does not have a tunable CCT LED, I hope this algorithm can spark a disscussion about the addition of some smarter features that Dyson offers eg. Motion sensing and object distance sensing with a ToF sensor.

## How the aglorithm works
Based on Dyson's advertised features, I have tried to replicate some of them in this algorithm. Currently there's no API's or accesible data that are publicly accesible, nor are there any equations that can estimate the aproximate CCT of the sun at a given location and time. Instead, I have gone through the mathmatic route. Hopfully this explanation will demistify my completly unreadable code.
### CCT Calculations
I have used a Quadratic formula to estimate the Colour Temperature of the sun, in  the form: *y = ax + bx + c*, Where y = CCT and x = Local Time. the crutical element to this equation is the use of sunset and sunrise times. when the sun rises and sets, the CCT is often at its lowest point, usually around 2000K, while Noon is at around 5000-6500K. we can construct this equation so that the parabola intersects 2000 in the y, and the sunrise/sunset time in the x. A parabola (Quadratic Graph) looks somthing like this:

<img src="D:\Programming\DIYson-SolarCycle\info_assets\parabola.png" alt="Parabola">

As the sunset and sunrise times chage during the year, the Module "Suntime" is used so that the Parabola is constantly chaging throughout the year. to facilitate this, another equation is used to calculate the equation, as seen below:

<img src="https://github.com/Joseph0M/DIYson-SolarCycle/blob/main/info_assets/parabola_equation.png" alt="Equation">
Where: 

**f(x)** = Sun's CCT
**x** = Local Time
**a1**,**b1** = (Sunrise Time, Sunrise CCT)
**a2**,**b2** = (Noon, Noon CCT)
**a3**,**b3** = (Sunset Time, Sunset CCT)
 And finally, this is outputted as a percentage of theminimum and maximum CCT that the LED can replicate

 ### Solar Insolation (Intensity)
 Compared to the CCT replication algorithm, there are many equations used to calculate the intensity of the sun if given the location and time. I will not cover most of this, as I am not a certified astrophysicist, nor could I verify that this equation is acurate based on supplied readings.
 the algorithm takes in the *Solar Constant* (1364 W/m^2), the *relative sun-earth distance* (1.1) and *atmospheric turbidity factor* (0.6). It also takes in the Latitude and Longitude of the user. the Intensity is then returned as a percentage, and can be used in conjunction with the age multiplier function.

as well as these features, values are always checked for violations of LED specs before being returned. As this algortihm is contained in a class, it can be inported, or intergrated into existing scripts fairly easily.




# Solar Tracking with the DIYson
The aim with this algorithm is to provide the capability of changing **CCT (Colour temperature)**  and **intensity** based on the sun's movement throughout the day. it also includes the age multiplier function that **varies the light intensity based on age**, replicating the feature from Dyson. Although the DIYson currently does not have a tunable CCT LED, I hope this algorithm can spark a discussion about the addition of some smarter features that Dyson offers, e.g., motion sensing and object distance sensing with a ToF sensor.


## How the aglorithm works
Based on Dyson's advertised features, I have tried to replicate some of them in this algorithm. Currently, there are no APIs or publicly accessible data, nor are there any equations that can estimate the approximate CCT of the sun at a given location and time. Instead, I have gone through the mathematical route. Hopfully this explanation will demistify my completely unreadable code.
### CCT Calculations
I have used a quadratic formula to estimate the Colour temperature of the sun, in  the form: *y = ax + bx + c*, Where y = CCT and x = local time. The crucial element of this equation is the use of sunset and sunrise times. When the sun rises and sets, the CCT is often at its lowest point, usually around 2000K, while noon is around 5000–6500K. We can construct this equation so that the parabola intersects 2000 in the y, and the sunrise/sunset time in the x. A parabola (quadratic graph) looks something like this:

# Image parabola

As the sunset and sunrise times change during the year, the module "Suntime" is used so that the parabola is constantly changing throughout the year. To facilitate this, another equation is used to calculate the equation, as seen below:

# Image equation

### Where:

* **f(x)** = Sun's CCT
* **x** = Local Time
* **a1**,**b1** = (Sunrise Time, Sunrise CCT)
* **a2**,**b2** = (Noon, Noon CCT)
* **a3**,**b3** = (Sunset Time, Sunset CCT)

And finally, this is returned as a percentage of the minimum and maximum CCT that the LED can replicate.

### Solar Insolation (Intensity)
Compared to the CCT replication algorithm, there are many equations used to calculate the intensity of the sun given the location and time. I will not cover most of this, as I am not a certified astrophysicist, nor could I verify that this equation is accurate based on the supplied readings.
The algorithm takes into account the *Solar Constant* (1364 W/m^2), the *relative sun-earth distance* (1.1), and *atmospheric turbidity factor* (0.6). It also takes in the latitude and longitude of the user. The intensity is then returned as a percentage and can be used in conjunction with the age multiplier function.

### Final Thoughts
Along with these features, values are always checked for violations of LED specs before being returned. As this algorithm is contained in a class, it can be imported or intergrated into existing scripts fairly easily.
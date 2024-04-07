## How to run Circuit Python on the QT Py SAMD21 

1. Plug in QT Py 
2. Download latest version of circuit python: https://circuitpython.org/board/qtpy_m0/

3. Tap the board's reset button twice to enter bootloader mode

4. Install CircuitPython by dragging the downloaded `.uf2` file into `QTPY_BOOT` (it will replace the existing `.uf2` file and automatically reboot)

5. Circuit python should now be installed and the device will show up in your computer's device list. Use the Mu editor [Mu Editor](https://codewith.mu/) (recommended) to edit and upload code to the board.

6. Using your file browser, delete the `lib` folder from the board's directory and recreate it (we do this as an easy way to ensure that the folder is completely empty)

7. Download the Adafruit libraries bundle version *9.x* from: https://circuitpython.org/libraries

8. Copy the following from the downloaded lib to the boards lib directory (all other libraries are already on the board by default):
  - adafruit_debouncer.mpy
  - adafruit_ticks.mpy (not sure why but you need this)

8. Either copy and paste the contents of [LED Control.py](DIYson/LED%20Control.py) or move the whole file onto the board, replacing the existing `.py` file.

9. Ensure there are no errors by saving the `.py` file in the Mu editor with the serial console open.
    
<br>
**More resources:**

[adafruit.com/adafruit-qt-py/circuitpython](https://learn.adafruit.com/adafruit-qt-py/circuitpython)  
[circuitpython.org/libraries](https://circuitpython.org/libraries)

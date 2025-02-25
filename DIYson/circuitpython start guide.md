## How to run Circuit Python on the QT Py ESP32-S2

1. Follow steps here to install CircuitPython: https://learn.adafruit.com/adafruit-qt-py-esp32-s2/circuitpython
2. Download the Adafruit libraries bundle version *9.x* from: https://circuitpython.org/libraries
3. Copy the following libraries to the `lib` folder:
- adafruit_debouncer.mpy
- adafruit_ticks.mpy
4. Copy the contents of [Code.py](DIYson/Code.py) or move the whole file onto the board, replacing the existing file.
5. Use your favorite editor to edit Code.py. Mu works well as-is. I personally use Visual Studio Code with the [CircuitPython v2](https://marketplace.visualstudio.com/items?itemName=wmerkens.vscode-circuitpython-v2) extensions for serial output.
<br>

**More resources**

[About Circuit Python](https://learn.adafruit.com/adafruit-qt-py/circuitpython)  
[More about the Adafruit QT Py ESP32-S2](https://learn.adafruit.com/adafruit-qt-py-esp32-s2/overview)
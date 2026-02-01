#python -m mpremote cp main.py :
#python -m mpremote connect COM7 repl
#python -m mpremote reset

#then press reset or 
import time
from machine import Pin

print("main.py running")

led = Pin(2, Pin.OUT)

while True:
    led.toggle()
    time.sleep(1)


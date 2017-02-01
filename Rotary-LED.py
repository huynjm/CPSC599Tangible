import RPi.GPIO as GPIO
from time import sleep
import os

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)

ROTP = 17
LED_1 = 2
LED_2 = 3
LED_3 = 4

GPIO.setup(ROTP, GPIO.IN)
GPIO.setup(LED_1, GPIO.OUT)
GPIO.setup(LED_2, GPIO.OUT)
GPIO.setup(LED_3, GPIO.OUT)

try:
    while True:
      if (GPIO.input(ROTP)):
        GPIO.output(LED_1, GPIO.LOW)
        sleep(0.5)
        GPIO.output(LED_2, GPIO.LOW)
        sleep(0.5)
        GPIO.output(LED_3, GPIO.LOW)
        sleep(0.5)
      else:
        omxplayer -o local start-pokedex.mp3
        GPIO.output(LED_1, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_2, GPIO.HIGH)
        sleep(0.5)
        GPIO.output(LED_3, GPIO.HIGH)
        sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()

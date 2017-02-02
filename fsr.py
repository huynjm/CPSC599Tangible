#!/usr/bin/env python

# Written by Limor "Ladyada" Fried for Adafruit Industries, (c) 2015
# This code is released into the public domain

import time
import os
import RPi.GPIO as GPIO
import pygame.mixer
from pygame.locals import *
from subprocess import call

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
DEBUG = 1

pygame.mixer.init()
piano = pygame.mixer.Sound("pokemon.mp3")
pokedex = pygame.mixer.Sound("start-pokedex.mp3")

# read SPI data from MCP3008 chip, 8 possible adc's (0 thru 7)
def readadc(adcnum, clockpin, mosipin, misopin, cspin):
        if ((adcnum > 7) or (adcnum < 0)):
                return -1
        GPIO.output(cspin, True)

        GPIO.output(clockpin, False)  # start clock low
        GPIO.output(cspin, False)     # bring CS low

        commandout = adcnum
        commandout |= 0x18  # start bit + single-ended bit
        commandout <<= 3    # we only need to send 5 bits here
        for i in range(5):
                if (commandout & 0x80):
                        GPIO.output(mosipin, True)
                else:
                        GPIO.output(mosipin, False)
                commandout <<= 1
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)

        adcout = 0
        # read in one empty bit, one null bit and 10 ADC bits
        for i in range(12):
                GPIO.output(clockpin, True)
                GPIO.output(clockpin, False)
                adcout <<= 1
                if (GPIO.input(misopin)):
                        adcout |= 0x1

        GPIO.output(cspin, True)
        
        adcout >>= 1       # first bit is 'null' so drop it
        return adcout

# change these as desired - they're the pins connected from the
# SPI port on the ADC to the Cobbler
SPICLK = 18
SPIMISO = 23
SPIMOSI = 24
SPICS = 25

# LED StartUp Pin numbers
ROTP = 19
LED_1 = 2
LED_2 = 3
LED_3 = 4

# set up the SPI interface pins
GPIO.setup(SPIMOSI, GPIO.OUT)
GPIO.setup(SPIMISO, GPIO.IN)
GPIO.setup(SPICLK, GPIO.OUT)
GPIO.setup(SPICS, GPIO.OUT)

# set up the LED StartUp interface pins
GPIO.setup(ROTP, GPIO.IN)
GPIO.setup(LED_1, GPIO.OUT)
GPIO.setup(LED_2, GPIO.OUT)
GPIO.setup(LED_3, GPIO.OUT)

# 10k trim pot connected to adc #0
potentiometer_adc = 0;
played = False
last_read = 1       # this keeps track of the last potentiometer value
tolerance = 5       # to keep from being jittery we'll only change
                    # volume when the pot has moved more than 5 'counts'

piano.play()

try:
	while True:		
			# we'll assume that the pot didn't move
			trim_pot_changed = False
			
			# read the analog pin
			trim_pot = readadc(potentiometer_adc, SPICLK, SPIMOSI, SPIMISO, SPICS)
			# how much has it changed since the last read?
			pot_adjust = abs(trim_pot - last_read)
			
			# if Rotary turned on, start up pokedex and trigger LED's
			if(GPIO.input(ROTP)):
				if (played == False):
					os.system("omxplayer -o hdmi start-pokedex.mp3")
					played = True
				GPIO.output(LED_1, GPIO.HIGH)
				time.sleep(0.5)
				GPIO.output(LED_2, GPIO.HIGH)
				time.sleep(0.5)
				GPIO.output(LED_3, GPIO.HIGH)
				time.sleep(0.5)
			else:
				played == False
				GPIO.output(LED_1, GPIO.LOW)
				time.sleep(0.5)
				GPIO.output(LED_2, GPIO.LOW)
				time.sleep(0.5)
				GPIO.output(LED_3, GPIO.LOW)
				time.sleep(0.5)				
				print("OFF")	
					
			if DEBUG:
					print "trim_pot:", trim_pot
					print "pot_adjust:", pot_adjust
					print "last_read", last_read

			if ( pot_adjust > tolerance ):
				   trim_pot_changed = True

			if DEBUG:
					print "trim_pot_changed", trim_pot_changed
					
			if(last_read == 0 and trim_pot > 0):
					piano.play()

			if ( trim_pot_changed ):
					set_volume = trim_pot / 10.24           # convert 10bit adc0 (0-1024) trim pot read into 0-100 volume level
					set_volume = round(set_volume)          # round out decimal value
					set_volume = int(set_volume)            # cast volume as integer
					
					if(trim_pot == 0):
						piano.stop()
										

					#print 'Volume = {volume}%' .format(volume = set_volume)
					set_vol_cmd = 'sudo amixer cset numid=1 -- {volume}% > /dev/null' .format(volume = set_volume)
					os.system(set_vol_cmd)  # set volume

					if DEBUG:
							print "set_volume", set_volume
							print "tri_pot_changed", set_volume

					# save the potentiometer reading for the next loop
					last_read = trim_pot
			

			# hang out and do nothing for a half second
			time.sleep(0.5)
except KeyboardInterrupt:
    pass
finally:
    GPIO.cleanup()

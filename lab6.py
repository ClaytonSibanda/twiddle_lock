
#!/usr/bin/python
# Importing modules
import spidev # To communicate with SPI devices
from time import sleep,strftime  # To add delay and display time
# Start SPI connection
spi = spidev.SpiDev() # Created an object
spi.open(0,0) 
spi.max_speed_hz=1000000
#setup gpio

import RPi.GPIO as GPIO
    
GPIO.setmode(GPIO.BOARD)
start_button=40
stop_button=38
frequency_button =37
display_button=36

GPIO.setup(start_button,GPIO.IN,pull_up_down=GPIO.PUD_UP)


isLocked = True
password= ['L',2,'R',4]

def is_unlocked(pattern):
    for i in range(len(pattern)):
        if  i==0 or i==2:
            if pattern[i]!=password[i]:
                return False
        if(i==1 or i==3):
            if round(pattern[i])!=password[i]:
                return False
    return True
            
                

# Read MCP3008 data
def analog_input(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

# Below function will convert data to voltage
def convert_volts(data):
	volts = (data * 3.3) / float(1023)
	volts = round(volts, 2) # Round off to 2 decimal places
	return volts


def get_time():
	return strftime("%H:%M:%S")
def delay():
   sleep(0.5)

while True:
	#temp_output = analog_input(0) # Reading from CH1
	#temp       = convert_temp(temp_output)
	pot_output= analog_input(1)#reads from channel 1 from the pot
	pot_volts = convert_volts(pot_output)#gets potentiometer voltages
        print(pot_output)
        
        if(GPIO.input(start_button)==0):
            print("start pressed")
            delay()

        pattern =['L',2.3,'L',4]
        if is_unlocked(pattern):
                print("unlocked")
        else:
            print("wrong password try again")
	sleep(0.5)
GPIO.cleanup() # release pins from this operation

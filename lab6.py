
#!/usr/bin/python
# Importing modules
import spidev # To communicate with SPI devices
from time import sleep,strftime, time  # To add delay and display time
from thread import start_new_thread


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

#delay function
def delay():
   sleep(1)

def getDirection(curr,prev):
    if curr>prev:
        return 'R'
    elif curr<prev:
        return 'L'
    else:
        return "No change"




u_line =True
l_line = False
pot_values=[]
pattern=[]
directions=[]
direction=''
start =False


def populate_pattern(symbol):
    pattern.append(symbol)

    
def read_pot_adc():
    global direction
    while True:
        if start:
            pot_output= analog_input(1)#reads from channel 1 from the pot
            pot_values.append(pot_output)

            
            if len(pot_values)>1:
                direction = getDirection(pot_values[len(pot_values)-1],pot_values[len(pot_values)-2])
                directions.append(direction)
                print("directions: {},direction: {}, pot_values: {} ".format(directions[len(directions)-3:],direction,pot_values[len(pot_values)-3:]))
            delay()




def get_first_symbol(dirs):
    for symbol in dirs:
        if(symbol) != 'No change':
            populate_pattern(symbol)
            break



start_time=0

   
pattern1 =['L',2.3,'L',4]
if len(pattern)>3:
    if is_unlocked(pattern1):
        print("unlocked")
    else:
        print("wrong password try again")

isPaused = False

def get_pause_status():
    global isPaused
    while True:
        if len(directions)>4 and directions[len(directions)-1]=="No change":
            isPaused = True
        else:
            isPaused = False


def start_helper_threads():
    #thread for monitoring no change symbol 
    try:
        start_new_thread(get_pause_status,())
    except:
        print("Error thread2 error")
    #thread monitoring the reading of the of the potentiometer
    try:
        start_new_thread(read_pot_adc,())
    except:
        print("Error adc thread error")


while len(pattern)!=4:
    if(GPIO.input(start_button)==0):
        if start:
            #reset the list
            directions[:]=[]
            pot_values[:]=[]
            pattern[:]=[]
            
        else:
            print("start pressed")
            start_time=time()
            start_helper_threads()
        start =True
        
    
    if  len(pattern)==0 and len(directions)>3:
        get_first_symbol(directions)
    
    if isPaused and len(pattern)==1:
        pattern.append(time()-start_time)
        start_time =time()-1
    if (not isPaused) and len(pattern)==2:
        pattern.append(directions[len(directions)-1])
    if isPaused and len(pattern)==3:
        pattern.append(time()-start_time)

    print("pattern:{}, isPaused: {}".format(pattern,isPaused))
        
    delay()

#check if the safe has been unlocked and give feedback to the user
if is_unlocked(pattern):
    print("YaaaY!!!!!!!!!!!!!!!!! you unlocked the safe you won $1000000")
else:
    print("wrong password please try again")




GPIO.cleanup() # release pins from this operation

#if __name__ == "__main__":
    #run main here



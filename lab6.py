
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
unlocked_led=38
locked_led=36



GPIO.setup(unlocked_led,GPIO.OUT)
GPIO.setup(locked_led,GPIO.OUT)
GPIO.setup(start_button,GPIO.IN,pull_up_down=GPIO.PUD_UP)

GPIO.output(unlocked_led,GPIO.HIGH)
GPIO.output(locked_led,GPIO.HIGH)

isLocked = True
password= ['L',10,'R',10]#combopassword
tol_set = set([8,10,11,9,12])

def is_correct(pattern):
    for i in range(len(pattern)):
        if  i==0 or i==2:
            if pattern[i]!=password[i]:
                return False
        if(i==1 or i==3):
            if round(pattern[i]) not in tol_set:
                return False
    return True
            
                

# Read MCP3008 data
def analog_input(channel):
	adc = spi.xfer2([1,(8+channel)<<4,0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

#delay function
def delay(seconds):
   sleep(seconds)

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
                #print("directions: {},direction: {}, pot_values: {} ".format(directions[len(directions)-3:],direction,pot_values[len(pot_values)-3:]))
                
            delay(0.5)




def get_first_symbol(dirs):
    for symbol in dirs:
        if(symbol) != 'No change':
            populate_pattern(symbol)
            break



start_time=0
isPaused = False
is_unlock = True #default value
   





def get_pause_status():
    global isPaused
    while True:
        if len(directions)>4 and directions[len(directions)-1]=="No change":
            isPaused = True
        else:
            isPaused = False
        if len(pattern)>3:
                break


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
            #delay(2)# pause for 2 seconds after pressing start i.e S  button
            start_helper_threads()
            delay(2)
            start_time=time()

        start =True
           
    if  len(pattern)==0 and len(directions)>1:
        get_first_symbol(directions)
    
    if isPaused and len(pattern)==1:
        pattern.append(time()-start_time)
        sleep(2)#allow the user to start turning another direction after 2 seconds
        start_time =time()
    if (not isPaused) and len(pattern)==2:
        pattern.append(directions[len(directions)-1])
    if isPaused and len(pattern)==3:
        pattern.append(time()-start_time)
    print("pattern:{}, isPaused: {}".format(pattern,isPaused))
        
    
        #check if the safe has been unlocked and give feedback to the user
if is_correct(pattern):
    if is_unlock:
        print("YaaaY!!!!!!!!!!!!!!!!! you unlocked the safe you won $1000000")
       
    else:
        print("YaaaaY!!!!!!!!!!!!! you locked the safe")

else:
    print("wrong password please try again")
is_unlock=!is_unlock


GPIO.cleanup() # release pins from this operation
sleep(1)#allow all the threads to finish


#if __name__ == "__main__":
    #run main here



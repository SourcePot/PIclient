import datapoolclient
import os
import time
import pkgutil
from threading import Timer

# Entry creation: The entry contains the (initial) Settings and Status. 
# Settings hold the initial data for settings creation on the server, i.e. a blueprint of the settings data structure.
# After the first data is received from the server, the "piclient" Settings data will be updated from the server data to control the "piclient". 
# Status contains only data to be sent from the "piclient" to the server.
# The entry structure is a php datapool flat array (dictionarry in Python) with the entry separator "||". 
# The Entry Content Settings and Status have a datapool defintion structure.
entry={'Group':'Town','Folder':'Address','Name':'Location'}
# ADD SETTINGS - mode
entry['Content||Settings||mode||@function']='select'
entry['Content||Settings||mode||@value']='alarm'
entry['Content||Settings||mode||@dataType']='string'
entry['Content||Settings||mode||@excontainer']=''
entry['Content||Settings||mode||@options||idle']='Idle'
entry['Content||Settings||mode||@options||capture']='Capture'
entry['Content||Settings||mode||@options||sms']='SMS'
entry['Content||Settings||mode||@options||alarm']='Alarm'
# ADD SETTINGS - cature time
entry['Content||Settings||captureTime||@function']='select'
entry['Content||Settings||captureTime||@value']='3600'
entry['Content||Settings||captureTime||@dataType']='int'
entry['Content||Settings||captureTime||@excontainer']='1'
entry['Content||Settings||captureTime||@options||10']='10sec'
entry['Content||Settings||captureTime||@options||60']='1min'
entry['Content||Settings||captureTime||@options||600']='10min'
entry['Content||Settings||captureTime||@options||3600']='1h'
entry['Content||Settings||captureTime||@options||36000']='10h'
# ADD SETTINGS - light
entry['Content||Settings||light||@function']='select'
entry['Content||Settings||light||@value']='0'
entry['Content||Settings||light||@dataType']='bool'
entry['Content||Settings||light||@excontainer']='1'
entry['Content||Settings||light||@options||0']='Off'
entry['Content||Settings||light||@options||1']='On'
# ADD SETTINGS - alarm
entry['Content||Settings||alarm||@function']='select'
entry['Content||Settings||alarm||@value']='0'
entry['Content||Settings||alarm||@dataType']='bool'
entry['Content||Settings||alarm||@excontainer']='1'
entry['Content||Settings||alarm||@options||0']='Off'
entry['Content||Settings||alarm||@options||1']='On'
# ADD SETTINGS - A
entry['Content||Settings||A||@function']='select'
entry['Content||Settings||A||@value']='0'
entry['Content||Settings||A||@dataType']='bool'
entry['Content||Settings||A||@excontainer']='1'
entry['Content||Settings||A||@options||0']='Off'
entry['Content||Settings||A||@options||1']='On'
# ADD SETTINGS - B
entry['Content||Settings||B||@function']='select'
entry['Content||Settings||B||@value']='0'
entry['Content||Settings||B||@dataType']='bool'
entry['Content||Settings||B||@excontainer']='1'
entry['Content||Settings||B||@options||0']='Off'
entry['Content||Settings||B||@options||1']='On'
# ADD STATUS - mode
entry['Content||Status||mode||@tag']='p'
entry['Content||Status||mode||@value']='idle'
entry['Content||Status||mode||@dataType']='string'
# ADD STATUS - timestamp
entry['Content||Status||timestamp||@tag']='p'
entry['Content||Status||timestamp||@value']='0'
entry['Content||Status||timestamp||@dataType']='int'
# ADD STATUS - captureTime
entry['Content||Status||captureTime||@tag']='p'
entry['Content||Status||captureTime||@value']='3600'
entry['Content||Status||captureTime||@dataType']='int'
# ADD STATUS - cpuTemperature
entry['Content||Status||cpuTemperature||@tag']='p'
entry['Content||Status||cpuTemperature||@value']='0'
entry['Content||Status||cpuTemperature||@dataType']='float'
# ADD STATUS - activity
entry['Content||Status||activity||@tag']='meter'
entry['Content||Status||activity||@min']='0'
entry['Content||Status||activity||@max']='20'
entry['Content||Status||activity||@low']='0'
entry['Content||Status||activity||@high']='3'
entry['Content||Status||activity||@value']='0'
entry['Content||Status||activity||@dataType']='int'
# ADD STATUS - light
entry['Content||Status||light||@tag']='meter'
entry['Content||Status||light||@min']='0'
entry['Content||Status||light||@max']='1'
entry['Content||Status||light||@value']='0'
entry['Content||Status||light||@dataType']='bool'
# ADD STATUS - alarm
entry['Content||Status||alarm||@tag']='meter'
entry['Content||Status||alarm||@min']='0'
entry['Content||Status||alarm||@max']='1'
entry['Content||Status||alarm||@high']='1'
entry['Content||Status||alarm||@value']='0'
entry['Content||Status||alarm||@dataType']='bool'
# ADD STATUS - escalate
entry['Content||Status||escalate||@tag']='meter'
entry['Content||Status||escalate||@min']='0'
entry['Content||Status||escalate||@max']='1'
entry['Content||Status||escalate||@high']='1'
entry['Content||Status||escalate||@value']='0'
entry['Content||Status||escalate||@dataType']='bool'
# ADD STATUS - A
entry['Content||Status||A||@tag']='meter'
entry['Content||Status||A||@min']='0'
entry['Content||Status||A||@max']='1'
entry['Content||Status||A||@value']='0'
entry['Content||Status||A||@dataType']='bool'
# ADD STATUS - B
entry['Content||Status||B||@tag']='meter'
entry['Content||Status||B||@min']='0'
entry['Content||Status||B||@max']='1'
entry['Content||Status||B||@value']='0'
entry['Content||Status||B||@dataType']='bool'
# ADD PARAMS - file
entry['Params||File||Name']=''
entry['Params||File||Extension']=''
entry['Params||File||MIME-Type']=''

# add internal lists
motionSensors={}
leds={}
strOutputs={}

dirs=datapoolclient.getDirs()

hasPiCamera=pkgutil.find_loader('picamera')
if hasPiCamera:
    import picamera

hasGpioZero=pkgutil.find_loader('gpiozero')
if hasGpioZero:
    from gpiozero import MotionSensor,CPUTemperature,LED

# ===================================== Outputs ===================================
def initOutputs():
    global leds
    if hasGpioZero:
        leds['Content||Settings||alarm||@value']=LED(17,initial_value=False)
        leds['Content||Settings||light||@value']=LED(18,initial_value=False)
        leds['Content||Settings||A||@value']=LED(22,initial_value=False)
        leds['Content||Settings||B||@value']=LED(23,initial_value=False)
    print('Client started')
initOutputs()

# process repsponse
def writeOutputs(response):
    global leds,entry
    if type(response) is not bool:
        for key,value in response.items():
            key=key+'||@value'
            if key in leds:
                if (int(value)>0):
                    leds[key].on()
                    entry[key]='1'
                else:
                    leds[key].off()
                    entry[key]='0'
            if key in strOutputs:
                if key=='console':
                    print(value)
            if key in entry:
                entry[key]=value
                #print(key+': '+str(entry[key]))

# ===================================== Sensors ===================================
def initInputs():
    global motionSensors
    if hasGpioZero:
        motionSensors['pirA']=MotionSensor(pin=27,pull_up=None,active_state=True)
        motionSensors['pirB']=MotionSensor(pin=24,pull_up=None,active_state=True)
initInputs()        

def readInputs():
    global entry
    entry['Date']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    entry['Content||Status||timestamp||@value']=time.time()
    entry['Content||Status||activity||@value']=activity
    entry['Content||Status||mode||@value']=entry['Content||Settings||mode||@value']
    entry['Content||Status||captureTime||@value']=entry['Content||Settings||captureTime||@value']
    for key,value in leds.items():
        entryKey=key.replace('Settings','Status')
        entry[entryKey]=str(int(leds[key].is_active))
    if hasGpioZero:
        entry['Content||Status||cpuTemperature||@value']=CPUTemperature().temperature
    return dict(entry)

# ===================================== Behaviour =================================
activity=0

def captureFileNames(filename):
    frame=0
    while frame<4:
        yield dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_'+str(frame)+'.jpg'
        frame+=1

busyCapturing=False
def capture(filename):
    global busyCapturing,leds
    busyCapturing=True
    if entry['Content||Settings||mode||@value']!='idle':
        leds['Content||Settings||light||@value'].on()
    captureEntry=readInputs()
    if hasPiCamera and entry['Content||Settings||mode||@value']!='idle':
        with picamera.PiCamera(framerate=2) as camera:
            camera.start_preview()
            time.sleep(1)
            camera.capture_sequence(captureFileNames(filename),use_video_port=False,resize=None)
            mediaItems2stack(captureEntry)
    busyCapturing=False
    if (int(entry['Content||Settings||light||@value'])==1):
        leds['Content||Settings||light||@value'].on()
    else:
        leds['Content||Settings||light||@value'].off()
 
def motionA():
    global busyCapturing,activity,leds,entry
    activity+=4
    if (busyCapturing==False):
        if entry['Content||Settings||mode||@value']=='alarm':
            leds['Content||Settings||alarm||@value'].on()
            entry['Content||Status||escalate||@value']='1'
        elif entry['Content||Settings||mode||@value']=='sms':
            entry['Content||Status||escalate||@value']='1'
        capture('motionA')
        entry['Content||Status||escalate||@value']='0'
        if (str(entry['Content||Settings||alarm||@value'])=='1'):
            leds['Content||Settings||alarm||@value'].on()
        else:
            leds['Content||Settings||alarm||@value'].off()
    
def motionB():
    global activity
    activity+=1
    
if 'pirA' in motionSensors:
    motionSensors['pirA'].when_motion=motionA
if 'pirB' in motionSensors:
    motionSensors['pirB'].when_motion=motionB

def updateActivity():
    global activity
    if (activity>0):
        activity-=1
    t=Timer(6,updateActivity)
    t.start()
updateActivity()

# ==== add media item and/or status data to stack and process the stack ===========

def mediaItems2stack(captureEntry):
    for file in os.listdir(dirs['media']):
        captureEntry['Tag']='media'
        fileNameComps=file.split('_')
        if (len(fileNameComps)==3):
            captureEntry['Content||Status||timestamp||@value']=fileNameComps[1]
            captureEntry['Params||File||Name']=file
            captureEntry['Params||File||Extension']='jpeg'
            captureEntry['Params||File||MIME-Type']='image/jpeg'
        else:
            captureEntry['Params||File||Name']=''
            captureEntry['Params||File||Extension']=''
            captureEntry['Params||File||MIME-Type']=''
        datapoolclient.add2stack(captureEntry,dirs['media']+'/'+file)
    
def statusPolling():
    captureEntry=readInputs()
    captureEntry['Tag']='status'
    datapoolclient.add2stack(captureEntry)
    t=Timer(4.7,statusPolling)
    t.start()
statusPolling()

def stackProcessingLoop():
    answer=datapoolclient.processStack()
    #print(datapoolclient.response)
    if type(answer) is bool:
        if answer==True:
            # Stack is empty
            t=Timer(1,stackProcessingLoop)
            writeOutputs(datapoolclient.response)
        else:
            # Server answer missing
            t=Timer(30.0,stackProcessingLoop)
    else:
        # Normal stack processing
        writeOutputs(datapoolclient.response)
        t=Timer(1.9,stackProcessingLoop)
    t.start()
stackProcessingLoop()

# ==== periodic capturing =========================================================
ticks=0
def periodicCapture():
    global ticks
    captureTime=int(entry['Content||Settings||captureTime||@value'])
    if (captureTime!=0):
        if (ticks % captureTime==0):
            if (busyCapturing==False):
                capture('capture')
    ticks+=1
    t=Timer(1.0,periodicCapture)
    t.start()
periodicCapture()

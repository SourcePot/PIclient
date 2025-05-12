import datapoolclient
import os
import time
import pkgutil
from threading import Timer

entry={'Group':'Town','Folder':'Street','Name':'Location'}
# settings
entry['Content||Settings||mode||@function']='select'
entry['Content||Settings||mode||@value']='alarm'
entry['Content||Settings||mode||@dataType']='string'
entry['Content||Settings||mode||@excontainer']=''
entry['Content||Settings||mode||@options||idle']='Idle'
entry['Content||Settings||mode||@options||capture']='Capture'
entry['Content||Settings||mode||@options||sms']='SMS'
entry['Content||Settings||mode||@options||alarm']='Alarm'

entry['Content||Settings||captureTime||@function']='select'
entry['Content||Settings||captureTime||@value']='3600'
entry['Content||Settings||captureTime||@dataType']='int'
entry['Content||Settings||captureTime||@excontainer']='1'
entry['Content||Settings||captureTime||@options||10']='10sec'
entry['Content||Settings||captureTime||@options||60']='1min'
entry['Content||Settings||captureTime||@options||600']='10min'
entry['Content||Settings||captureTime||@options||3600']='1h'
entry['Content||Settings||captureTime||@options||36000']='10h'

entry['Content||Settings||light||@function']='select'
entry['Content||Settings||light||@value']='0'
entry['Content||Settings||light||@dataType']='bool'
entry['Content||Settings||light||@excontainer']='1'
entry['Content||Settings||light||@options||0']='Off'
entry['Content||Settings||light||@options||1']='On'

entry['Content||Settings||alarm||@function']='select'
entry['Content||Settings||alarm||@value']='0'
entry['Content||Settings||alarm||@dataType']='bool'
entry['Content||Settings||alarm||@excontainer']='1'
entry['Content||Settings||alarm||@options||0']='Off'
entry['Content||Settings||alarm||@options||1']='On'

entry['Content||Settings||A||@function']='select'
entry['Content||Settings||A||@value']='0'
entry['Content||Settings||A||@dataType']='bool'
entry['Content||Settings||A||@excontainer']='1'
entry['Content||Settings||A||@options||0']='Off'
entry['Content||Settings||A||@options||1']='On'

entry['Content||Settings||B||@function']='select'
entry['Content||Settings||B||@value']='0'
entry['Content||Settings||B||@dataType']='bool'
entry['Content||Settings||B||@excontainer']='1'
entry['Content||Settings||B||@options||0']='Off'
entry['Content||Settings||B||@options||1']='On'
# status
entry['Content||Status||mode||@tag']='p'
entry['Content||Status||mode||@value']='idle'
entry['Content||Status||mode||@dataType']='string'

entry['Content||Status||timestamp||@tag']='p'
entry['Content||Status||timestamp||@value']='0'
entry['Content||Status||timestamp||@dataType']='int'

entry['Content||Status||captureTime||@tag']='p'
entry['Content||Status||captureTime||@value']='3600'
entry['Content||Status||captureTime||@dataType']='int'

entry['Content||Status||cpuTemperature||@tag']='p'
entry['Content||Status||cpuTemperature||@value']='0'
entry['Content||Status||cpuTemperature||@dataType']='float'

entry['Content||Status||activity||@tag']='meter'
entry['Content||Status||activity||@min']='0'
entry['Content||Status||activity||@max']='20'
entry['Content||Status||activity||@low']='0'
entry['Content||Status||activity||@high']='3'
entry['Content||Status||activity||@value']='0'
entry['Content||Status||activity||@dataType']='int'

entry['Content||Status||light||@tag']='meter'
entry['Content||Status||light||@min']='0'
entry['Content||Status||light||@max']='1'
entry['Content||Status||light||@value']='0'
entry['Content||Status||light||@dataType']='bool'

entry['Content||Status||alarm||@tag']='meter'
entry['Content||Status||alarm||@min']='0'
entry['Content||Status||alarm||@max']='1'
entry['Content||Status||alarm||@high']='1'
entry['Content||Status||alarm||@value']='0'
entry['Content||Status||alarm||@dataType']='bool'

entry['Content||Status||escalate||@tag']='meter'
entry['Content||Status||escalate||@min']='0'
entry['Content||Status||escalate||@max']='1'
entry['Content||Status||escalate||@high']='1'
entry['Content||Status||escalate||@value']='0'
entry['Content||Status||escalate||@dataType']='bool'

entry['Content||Status||A||@tag']='meter'
entry['Content||Status||A||@min']='0'
entry['Content||Status||A||@max']='1'
entry['Content||Status||A||@value']='0'
entry['Content||Status||A||@dataType']='bool'

entry['Content||Status||B||@tag']='meter'
entry['Content||Status||B||@min']='0'
entry['Content||Status||B||@max']='1'
entry['Content||Status||B||@value']='0'
entry['Content||Status||B||@dataType']='bool'

entry['Content||Status||Msg||@tag']='p'
entry['Content||Status||Msg||@value']='Started'
entry['Content||Status||Msg||@dataType']='string'

# file
entry['Params||File||Name']=''
entry['Params||File||Extension']=''
entry['Params||File||MIME-Type']=''

strOutputs={'Content||Settings||Feedback':''}

dirs=datapoolclient.getDirs()

hasPiCamera=pkgutil.find_loader('picamera')
if hasPiCamera:
    import picamera

hasGpioZero=pkgutil.find_loader('gpiozero')
if hasGpioZero:
    from gpiozero import MotionSensor,CPUTemperature,LED
else:
    print('Problem: gpiozero missing')
    
# ===================================== Outputs ===================================
def setEntry(key,value):
    global entry
    if key in entry:
        if (type(value) is bool):
            entry[key]=str(int(value))
        else:
            entry[key]=str(value)
leds={}

def initOutputs():
    global leds
    if hasGpioZero:
        leds['Content||Settings||alarm||@value']=LED(17,initial_value=False)
        leds['Content||Settings||light||@value']=LED(18,initial_value=False)
        leds['Content||Settings||A||@value']=LED(22,initial_value=False)
        leds['Content||Settings||B||@value']=LED(23,initial_value=False)

initOutputs()

# process repsponse
def writeOutputs(response):
    if type(response) is not bool:
        for key,value in response.items():
            if '||Settings||' in key:
                key=key+'||@value'
                if key in entry:
                    setEntry(key,value)
                if key in leds:
                    setLed(key,value)
                if key in strOutputs:
                    print(key+str(value))

def setLed(key,value):
    global leds
    if key in leds:
        if (int(value)>0):
            leds[key].on()
            pass
        else:
            leds[key].off()
            pass

# ===================================== Sensors ===================================
def readLeds():
    for key in leds:
        entryKey=key.replace('||Settings||','||Status||')
        setEntry(entryKey,leds[key].is_active)

def readInputs():
    readLeds()
    setEntry('Date',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    setEntry('Content||Status||timestamp||@value',time.time())
    setEntry('Content||Status||mode||@value',entry['Content||Settings||mode||@value'])
    setEntry('Content||Status||captureTime||@value',entry['Content||Settings||captureTime||@value'])
    if hasGpioZero:
        setEntry('Content||Status||cpuTemperature||@value',CPUTemperature().temperature)
    return dict(entry)

# ===================================== Behaviour =================================

def captureFileNames(filename):
    frame=0
    while frame<4:
        yield dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_'+str(frame)+'.jpg'
        frame+=1

busyCapturing=False

def capture(filename):
    global busyCapturing
    if busyCapturing==False:
        busyCapturing=True
        if entry['Content||Settings||mode||@value']!='idle':
            setLed('Content||Settings||light||@value',1)
        captureEntry=readInputs()
        if hasPiCamera and entry['Content||Settings||mode||@value']!='idle':
            with picamera.PiCamera(framerate=2) as camera:
                camera.start_preview()
                time.sleep(1)
                camera.capture_sequence(captureFileNames(filename),use_video_port=False,resize=None)
                mediaItems2stack(captureEntry)
        if (int(entry['Content||Settings||light||@value'])==1):
            setLed('Content||Settings||light||@value',1)
        else:
            setLed('Content||Settings||light||@value',0)
        busyCapturing=False
    else:
        print('Too busy, skipped capturing')
 
def motionA():
    addActivity(4)
    if entry['Content||Settings||mode||@value']=='alarm':
        setLed('Content||Settings||alarm||@value',1)
        setEntry('Content||Status||escalate||@value',1)
    elif entry['Content||Settings||mode||@value']=='sms':
        setEntry('Content||Status||escalate||@value',1)
    capture('motionA')
    setEntry('Content||Status||escalate||@value',0)
    if (int(entry['Content||Settings||alarm||@value'])==1):
        setLed('Content||Settings||alarm||@value',1)
    else:
        setLed('Content||Settings||alarm||@value',0)
    
def motionB():
    print('Motion B')
    addActivity(1)

if hasGpioZero:
    pirA=MotionSensor(27)
    pirA.when_motion=motionA
    pirB=MotionSensor(4)
    pirB=when_motion=motionB

print('Client initialized')

activity=0

def addActivity(add):
    global activity
    if (add>0):
        activity=activity+add
    elif (activity>0):
        activity=activity+add
    else:
        activity=0
    setEntry('Content||Status||activity||@value',activity)

def updateActivityTimer():
    addActivity(-1)
    t=Timer(6,updateActivityTimer)
    t.start()
updateActivityTimer()

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
        setEntry('Content||Status||Msg||@value','')
    
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
            capture('capture')
    ticks+=1
    t=Timer(1.0,periodicCapture)
    t.start()
periodicCapture()

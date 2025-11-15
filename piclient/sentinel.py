import datapoolclient
import os
import time
import pkgutil
from threading import Timer
from picamera2 import Picamera2,Preview
from picamera2.encoders import H264Encoder
from picamera2.outputs import FfmpegOutput
from gpiozero import MotionSensor,CPUTemperature,LED

town='Town'
address='Address'
location='Location'

entry={'Settings||Group':town,'Settings||Folder':address,'Settings||Name':location,'Status||Group':town,'Status||Folder':address,'Status||Name':location}
# settings
entry['Settings||Content||Settings||mode||@function']='select'
entry['Settings||Content||Settings||mode||@value']='sms'
entry['Settings||Content||Settings||mode||@dataType']='string'
entry['Settings||Content||Settings||mode||@excontainer']='0'
entry['Settings||Content||Settings||mode||@options||idle']='Idle'
entry['Settings||Content||Settings||mode||@options||capture']='Capture'
entry['Settings||Content||Settings||mode||@options||sms']='SMS'
entry['Settings||Content||Settings||mode||@options||alarm']='Alarm'
entry['Settings||Content||Settings||mode||@options||video']='Video'

entry['Settings||Content||Settings||captureTime||@function']='select'
entry['Settings||Content||Settings||captureTime||@value']='3600'
entry['Settings||Content||Settings||captureTime||@dataType']='int'
entry['Settings||Content||Settings||captureTime||@excontainer']='0'
entry['Settings||Content||Settings||captureTime||@options||10']='10sec'
entry['Settings||Content||Settings||captureTime||@options||60']='1min'
entry['Settings||Content||Settings||captureTime||@options||600']='10min'
entry['Settings||Content||Settings||captureTime||@options||3600']='1h'
entry['Settings||Content||Settings||captureTime||@options||36000']='10h'

entry['Settings||Content||Settings||light||@function']='select'
entry['Settings||Content||Settings||light||@value']='0'
entry['Settings||Content||Settings||light||@dataType']='bool'
entry['Settings||Content||Settings||light||@excontainer']='0'
entry['Settings||Content||Settings||light||@options||0']='Off'
entry['Settings||Content||Settings||light||@options||1']='On'

entry['Settings||Content||Settings||alarm||@function']='select'
entry['Settings||Content||Settings||alarm||@value']='0'
entry['Settings||Content||Settings||alarm||@dataType']='bool'
entry['Settings||Content||Settings||alarm||@excontainer']='0'
entry['Settings||Content||Settings||alarm||@options||0']='Off'
entry['Settings||Content||Settings||alarm||@options||1']='On'

entry['Settings||Content||Settings||A||@function']='select'
entry['Settings||Content||Settings||A||@value']='0'
entry['Settings||Content||Settings||A||@dataType']='bool'
entry['Settings||Content||Settings||A||@excontainer']='0'
entry['Settings||Content||Settings||A||@options||0']='Off'
entry['Settings||Content||Settings||A||@options||1']='On'

entry['Settings||Content||Settings||B||@function']='select'
entry['Settings||Content||Settings||B||@value']='0'
entry['Settings||Content||Settings||B||@dataType']='bool'
entry['Settings||Content||Settings||B||@excontainer']='0'
entry['Settings||Content||Settings||B||@options||0']='Off'
entry['Settings||Content||Settings||B||@options||1']='On'
# status
entry['Status||Content||Status||mode||@tag']='p'
entry['Status||Content||Status||mode||@value']='idle'
entry['Status||Content||Status||mode||@dataType']='string'

entry['Status||Content||Status||captureTime||@tag']='p'
entry['Status||Content||Status||captureTime||@value']='3600'
entry['Status||Content||Status||captureTime||@dataType']='int'

entry['Status||Content||Status||activity||@tag']='meter'
entry['Status||Content||Status||activity||@yMin']='0'
entry['Status||Content||Status||activity||@yMax']='20'
entry['Status||Content||Status||activity||@min']='0'
entry['Status||Content||Status||activity||@max']='20'
entry['Status||Content||Status||activity||@color']='green'
entry['Status||Content||Status||activity||@label']='INIT'
entry['Status||Content||Status||activity||@value']='0'
entry['Status||Content||Status||activity||@isSignal']='1'
entry['Status||Content||Status||activity||@dataType']='int'

entry['Status||Content||Status||activityB||@tag']='meter'
entry['Status||Content||Status||activityB||@yMin']='0'
entry['Status||Content||Status||activityB||@yMax']='20'
entry['Status||Content||Status||activityB||@min']='0'
entry['Status||Content||Status||activityB||@max']='20'
entry['Status||Content||Status||activityB||@color']='blue'
entry['Status||Content||Status||activityB||@label']='INIT'
entry['Status||Content||Status||activityB||@value']='0'
entry['Status||Content||Status||activityB||@isSignal']='1'
entry['Status||Content||Status||activityB||@dataType']='int'

entry['Status||Content||Status||escalate||@class']='SourcePot\\Datapool\\Tools\\MiscTools'
entry['Status||Content||Status||escalate||@function']='bool2html'
entry['Status||Content||Status||escalate||@yMin']='1'
entry['Status||Content||Status||escalate||@yMax']='0'
entry['Status||Content||Status||escalate||@color']='blue'
entry['Status||Content||Status||escalate||@value']='0'
entry['Status||Content||Status||escalate||@isSignal']='1'
entry['Status||Content||Status||escalate||@dataType']='bool'

entry['Status||Content||Status||light||@class']='SourcePot\\Datapool\\Tools\\MiscTools'
entry['Status||Content||Status||light||@function']='bool2html'
entry['Status||Content||Status||light||@yMin']='1'
entry['Status||Content||Status||light||@yMax']='0'
entry['Status||Content||Status||light||@color']='blue'
entry['Status||Content||Status||light||@value']='0'
entry['Status||Content||Status||light||@isSignal']='1'
entry['Status||Content||Status||light||@dataType']='bool'

entry['Status||Content||Status||alarm||@class']='SourcePot\\Datapool\\Tools\\MiscTools'
entry['Status||Content||Status||alarm||@function']='bool2html'
entry['Status||Content||Status||alarm||@yMin']='1'
entry['Status||Content||Status||alarm||@yMax']='0'
entry['Status||Content||Status||alarm||@color']='red'
entry['Status||Content||Status||alarm||@value']='0'
entry['Status||Content||Status||alarm||@isSignal']='1'
entry['Status||Content||Status||alarm||@dataType']='bool'

entry['Status||Content||Status||A||@class']='SourcePot\\Datapool\\Tools\\MiscTools'
entry['Status||Content||Status||A||@function']='bool2html'
entry['Status||Content||Status||A||@yMin']='1'
entry['Status||Content||Status||A||@yMax']='0'
entry['Status||Content||Status||A||@color']='blue'
entry['Status||Content||Status||A||@value']='0'
entry['Status||Content||Status||A||@dataType']='bool'

entry['Status||Content||Status||B||@class']='SourcePot\\Datapool\\Tools\\MiscTools'
entry['Status||Content||Status||B||@function']='bool2html'
entry['Status||Content||Status||B||@yMin']='1'
entry['Status||Content||Status||B||@yMax']='0'
entry['Status||Content||Status||B||@color']='blue'
entry['Status||Content||Status||B||@value']='0'
entry['Status||Content||Status||B||@dataType']='bool'

entry['Status||Content||Status||timestamp||@tag']='p'
entry['Status||Content||Status||timestamp||@value']='0'
entry['Status||Content||Status||timestamp||@dataType']='int'

entry['Status||Content||Status||cpuTemperature||@tag']='p'
entry['Status||Content||Status||cpuTemperature||@yMin']='30'
entry['Status||Content||Status||cpuTemperature||@yMax']='100'
entry['Status||Content||Status||cpuTemperature||@value']='0'
entry['Status||Content||Status||cpuTemperature||@isSignal']='1'
entry['Status||Content||Status||cpuTemperature||@dataType']='float'

entry['Status||Content||Status||Msg||@tag']='p'
entry['Status||Content||Status||Msg||@value']='Started'
entry['Status||Content||Status||Msg||@dataType']='string'

# file
entry['Status||Params||File||Name']=''
entry['Status||Params||File||Extension']=''
entry['Status||Params||File||MIME-Type']=''

strOutputs={'Settings||Content||Settings||Feedback':''}

dirs=datapoolclient.getDirs()
    
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
    leds['Settings||Content||Settings||alarm||@value']=LED(17,initial_value=False)
    leds['Settings||Content||Settings||light||@value']=LED(18,initial_value=False)
    leds['Settings||Content||Settings||A||@value']=LED(22,initial_value=False)
    leds['Settings||Content||Settings||B||@value']=LED(23,initial_value=False)

initOutputs()

# process repsponse
def writeOutputs(response):
    if type(response) is not bool:
        for key,value in response.items():
            if '||Settings||' in key:
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
camera=Picamera2()

def readLeds():
    for key in leds:
        entryKey=key.replace('Settings||','Status||')
        setEntry(entryKey,leds[key].is_active)

def readInputs():
    readLeds()
    setEntry('Date',time.strftime('%Y-%m-%d %H:%M:%S',time.localtime()))
    setEntry('Status||Content||Status||timestamp||@value',int(time.time()))
    setEntry('Status||Content||Status||mode||@value',entry['Settings||Content||Settings||mode||@value'])
    setEntry('Status||Content||Status||captureTime||@value',entry['Settings||Content||Settings||captureTime||@value'])
    setEntry('Status||Content||Status||cpuTemperature||@value',CPUTemperature().temperature)
    return dict(entry)

# ===================================== Behaviour =================================

busyCapturing=False

def capture(filename):
    global busyCapturing
    if busyCapturing==False:
        busyCapturing=True
        activateCamera=entry['Settings||Content||Settings||mode||@value']!='idle'
        # Activate light
        if activateCamera and entry['Settings||Content||Settings||mode||@value']!='capture' and entry['Settings||Content||Settings||mode||@value']!='video':
            setLed('Settings||Content||Settings||light||@value',1)
        # Prepare capture entry
        captureEntry=readInputs()
        if (activateCamera):
            # set entry lifetime
            if entry['Settings||Content||Settings||mode||@value']=='sms':
                captureEntry['lifetime']=6048000
            elif entry['Settings||Content||Settings||mode||@value']=='alarm':
                captureEntry['lifetime']=31536000
            elif entry['Settings||Content||Settings||mode||@value']=='video':
                captureEntry['lifetime']=304800
            else:
                captureEntry['lifetime']=604800    
            # Capture images/video + status
            captureEntry['Tag']='media'
            # set camera
            if entry['Settings||Content||Settings||mode||@value']=='video':
                config=camera.create_video_configuration()
                camera.configure(config)
                encoder=H264Encoder(10000000)
                output=FfmpegOutput(dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_1.mp4',audio=False)
                camera.start_recording(encoder,output)
                time.sleep(5)
                camera.stop_recording()
            else:
                config=camera.create_still_configuration(main={"size":(1280,720)})
                camera.configure(config)
                camera.start(show_preview=False)
                time.sleep(1)
                camera.capture_file(dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_1.jpg')
                mediaItems2stack(captureEntry)
                time.sleep(1)
                camera.capture_file(dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_2.jpg')
            # wrap-up
            camera.stop()
            mediaItems2stack(captureEntry)
        else:
            # Capture status only
            captureEntry['Tag']='status'
            datapoolclient.add2stack(captureEntry)
        busyCapturing=False
    else:
        print('Too busy, skipped capturing')
 
def motionA():
    #print('Motion A')
    if entry['Settings||Content||Settings||mode||@value']=='alarm':
        setLed('Settings||Content||Settings||alarm||@value',1)
        setEntry('Status||Content||Status||escalate||@value',1)
        activityType='alarm';
    elif entry['Settings||Content||Settings||mode||@value']=='sms':
        setEntry('Status||Content||Status||escalate||@value',1)
        activityType='sms';
    else:
        activityType='motion'
    addActivity(2,activityType)
    capture('motionA')
    setEntry('Status||Content||Status||escalate||@value',0)
    # reset alarm
    if (int(entry['Settings||Content||Settings||alarm||@value'])==1):
        setLed('Settings||Content||Settings||alarm||@value',1)
    else:
        setLed('Settings||Content||Settings||alarm||@value',0)
    # reset light
    if (int(entry['Settings||Content||Settings||light||@value'])==1):
        setLed('Settings||Content||Settings||light||@value',1)
    else:
        setLed('Settings||Content||Settings||light||@value',0)
    
def motionB():
    #print('Motion B')
    addActivityB(2,'motion')

pirA=MotionSensor(27)
pirA.when_motion=motionA
pirB=MotionSensor(24)
pirB.when_motion=motionB

print('Client initialized')

activity=0
def addActivity(add,label):
    global activity
    activity=activity+add
    if (activity<0):
        activity=0
    setEntry('Status||Content||Status||activity||@value',activity)
    setEntry('Status||Content||Status||activity||@label',label)
    if (label=='capture'):
        setEntry('Status||Content||Status||activity||@color','#03f')
    elif (label=='motion'):
        setEntry('Status||Content||Status||activity||@color','#3d0')
    elif (label=='sms'):
        setEntry('Status||Content||Status||activity||@color','#f80')
    elif (label=='alarm'):
        setEntry('Status||Content||Status||activity||@color','#f00')
    else:
        setEntry('Status||Content||Status||activity||@color','#efe')

activityB=0
def addActivityB(add,label):
    global activityB
    activityB=activityB+add
    if (activityB<0):
        activityB=0
    setEntry('Status||Content||Status||activityB||@value',activityB)
    setEntry('Status||Content||Status||activityB||@label',label)
    setEntry('Status||Content||Status||activity||@color','#03f')

# ==== add media item and/or status data to stack and process the stack ===========

def mediaItems2stack(captureEntry):
    for file in os.listdir(dirs['media']):
        fileNameComps=file.split('_')
        if (len(fileNameComps)==3):
            captureEntry['Status||Content||Status||timestamp||@value']=fileNameComps[1]
            captureEntry['Status||Params||File||Name']=file
            if "jpg" in file:
                captureEntry['Status||Params||File||Extension']='jpg'
                captureEntry['Status||Params||File||MIME-Type']='image/jpeg'
            elif "mp4" in file:
                captureEntry['Status||Params||File||Extension']='mp4'
                captureEntry['Status||Params||File||MIME-Type']='video/mp4'    
        else:
            captureEntry['Status||Params||File||Name']=''
            captureEntry['Status||Params||File||Extension']=''
            captureEntry['Status||Params||File||MIME-Type']=''
        datapoolclient.add2stack(captureEntry,dirs['media']+'/'+file)
        setEntry('Status||Content||Status||Msg||@value','')
    
def statusPolling():
    addActivity(-1,'polling')
    addActivityB(-1,'polling')
    if busyCapturing==False:
        setEntry('Status||Content||Status||activity||@isSignal','0')
        setEntry('Status||Content||Status||activityB||@isSignal','1')
        captureEntry=readInputs()
        captureEntry['Tag']='status'
        captureEntry['lifetime']=300
        datapoolclient.add2stack(captureEntry)
        setEntry('Status||Content||Status||activity||@isSignal','1')
        setEntry('Status||Content||Status||activityB||@isSignal','1')
    t=Timer(4.9,statusPolling)
    t.start()
statusPolling()

def stackProcessingLoop():
    answer=datapoolclient.processStack()
    #print(datapoolclient.response)
    #print(answer)
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
        t=Timer(1.4,stackProcessingLoop)
    t.start()
stackProcessingLoop()

# ==== periodic capturing =========================================================
ticks=0
def periodicCapture():
    global ticks
    captureTime=int(entry['Settings||Content||Settings||captureTime||@value'])
    if (captureTime!=0):
        if (ticks % captureTime==0 and entry['Settings||Content||Settings||mode||@value']!='idle'):
            addActivity(0,'capture')
            capture('capture')
    ticks+=1
    t=Timer(1.0,periodicCapture)
    t.start()
periodicCapture()

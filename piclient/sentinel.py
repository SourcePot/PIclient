# Pi location
TOWN='E.g. enter the town here...'
ADDRESS='E.g. enter the house o and street here....'
LOCATION='E.g. enter the building here...'

GEO={'lat':'***','lon':'***'}

import os
import time
from threading import Timer
import datapoolclient

# I2C Bus Library, see https://pypi.org/project/smbus2/
try:
    import smbus2
    i2cBusOk=True
except ImportError:
    i2cBusOk=False
    datapoolclient.addLog({'warning':'Module smbus2 missing'})
    
# bme280 Sensor Library, see https://pypi.org/project/bme280/
try:
    import bme280
    bme280Ok=i2cBusOk
except ImportError:
    bme280Ok=False
    datapoolclient.addLog({'warning':'Module bme280 missing'})

# Camera Library, see https://pypi.org/project/picamera2/
try:
    from picamera2 import Picamera2
    from picamera2.encoders import H264Encoder
    from picamera2.outputs import FfmpegOutput
    cameraOk=True
except ImportError:
    print('Module picamera2 missing, exiting')
    cameraOk=False

# GPIO library, see https://pypi.org/project/gpiozero/
try:
    from gpiozero import MotionSensor,CPUTemperature,LED
except ImportError:
    print('Module gpiozero missing, exiting')
    exit(1)

print('Imports done')

if i2cBusOk==True:
    # BME280 sensor ADDRESS (default ADDRESS)
    I2C_ADDRESS = 0x76
    # Initialize I2C bus
    try:
        bus = smbus2.SMBus(1)
    except FileNotFoundError:
        print('SMBus file not found')
        i2cBusOk=False
        bme280Ok=False

if bme280Ok==True:
    # Load calibration parameters
    calibration_params = bme280.load_calibration_params(bus, I2C_ADDRESS)

# ========== Entry template consisting of the selector fields, settings and status fields ==========
# selector
entry={'Settings||Group':TOWN,'Settings||Folder':ADDRESS,'Settings||Name':LOCATION,'Status||Group':TOWN,'Status||Folder':ADDRESS,'Status||Name':LOCATION}
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

# status
entry['Status||Content||Status||mode||@tag']='p'
entry['Status||Content||Status||mode||@value']='idle'
entry['Status||Content||Status||mode||@dataType']='string'

entry['Status||Content||Status||captureTime||@tag']='p'
entry['Status||Content||Status||captureTime||@value']='3600'
entry['Status||Content||Status||captureTime||@dataType']='int'

entry['Status||Content||Status||activity||@tag']='meter'
entry['Status||Content||Status||activity||@color']='green'
entry['Status||Content||Status||activity||@label']='INIT'
entry['Status||Content||Status||activity||@value']='0'
entry['Status||Content||Status||activity||@isSignal']='1'
entry['Status||Content||Status||activity||@dataType']='int'

entry['Status||Content||Status||activityB||@tag']='meter'
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

entry['Status||Content||Status||timestamp||@tag']='p'
entry['Status||Content||Status||timestamp||@value']='0'
entry['Status||Content||Status||timestamp||@dataType']='int'

entry['Status||Content||Status||cpuTemperature||@tag']='p'
entry['Status||Content||Status||cpuTemperature||@value']='0'
entry['Status||Content||Status||cpuTemperature||@isSignal']='1'
entry['Status||Content||Status||cpuTemperature||@dataType']='float'

entry['Status||Content||Status||lat||@tag']='p'
entry['Status||Content||Status||lat||@value']=GEO['lat']
entry['Status||Content||Status||lat||@isSignal']='0'
entry['Status||Content||Status||lat||@dataType']='float'

entry['Status||Content||Status||lon||@tag']='p'
entry['Status||Content||Status||lon||@value']=GEO['lon']
entry['Status||Content||Status||lon||@isSignal']='0'
entry['Status||Content||Status||lon||@dataType']='float'

if bme280Ok==True:
    entry['Status||Content||Status||temperature_celsius||@tag']='p'
    entry['Status||Content||Status||temperature_celsius||@yMin']='-10'
    entry['Status||Content||Status||temperature_celsius||@yMax']='50'
    entry['Status||Content||Status||temperature_celsius||@value']='0'
    entry['Status||Content||Status||temperature_celsius||@isSignal']='1'
    entry['Status||Content||Status||temperature_celsius||@dataType']='float'

    entry['Status||Content||Status||humidity||@tag']='p'
    entry['Status||Content||Status||humidity||@value']='0'
    entry['Status||Content||Status||humidity||@isSignal']='1'
    entry['Status||Content||Status||humidity||@dataType']='float'

    entry['Status||Content||Status||pressure||@tag']='p'
    entry['Status||Content||Status||pressure||@value']='0'
    entry['Status||Content||Status||pressure||@isSignal']='1'
    entry['Status||Content||Status||pressure||@dataType']='float'

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
    if bme280Ok==True:
        # Extract temperature, pressure, humidity, and corresponding timestamp
        data = bme280.sample(bus, I2C_ADDRESS, calibration_params)
        entry['Status||Content||Status||temperature_celsius||@value']=data.temperature
        entry['Status||Content||Status||humidity||@value']=data.humidity
        entry['Status||Content||Status||pressure||@value']=data.pressure    
    return dict(entry)

if cameraOk==True:
    camera=Picamera2()

busyCapturing=False
serverConnectionFailure=False

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
        if (activateCamera and cameraOk==True):
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
                config=camera.create_video_configuration(main={"size":(720,480)})
                camera.configure(config)
                encoder=H264Encoder(10000000)
                output=FfmpegOutput(dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_1.mp4',audio=False)
                camera.start_recording(encoder,output)
                time.sleep(5)
                camera.stop_recording()
            else:
                config=camera.create_still_configuration(main={"size":(2592,1944)})
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
        time.sleep(3)
        busyCapturing=False
    else:
        datapoolclient.addLog({'info':'Too busy, skipped capturing'})
 
# ===================================== Behaviour =================================

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
            captureEntry['Status||Params||File||Name']='__TODELETE__'
            captureEntry['Status||Params||File||Extension']='__TODELETE__'
            captureEntry['Status||Params||File||MIME-Type']='__TODELETE__'
        datapoolclient.add2stack(captureEntry,dirs['media']+'/'+file)
        setEntry('Status||Content||Status||Msg||@value','')
    
def statusPolling():
    addActivity(-1,'polling')
    addActivityB(-1,'polling')
    if busyCapturing==False and serverConnectionFailure==False:
        # select if activity during status polling should be treated as signal
        setEntry('Status||Content||Status||activity||@isSignal','0')
        setEntry('Status||Content||Status||activityB||@isSignal','1')
        captureEntry=readInputs()
        # finalize entry
        captureEntry['Tag']='status'
        captureEntry['lifetime']=300
        datapoolclient.add2stack(captureEntry)
        # reset to stadard if activity should be treated as signal
        setEntry('Status||Content||Status||activity||@isSignal','1')
        setEntry('Status||Content||Status||activityB||@isSignal','1')
        t=Timer(7.9,statusPolling)
    else:
        t=Timer(21.9,statusPolling)
    t.start()
statusPolling()

def stackProcessingLoop():
    global serverConnectionFailure
    answer=datapoolclient.processStack()
    #print(datapoolclient.response)
    #print(answer)
    if type(answer) is bool:
        if answer==True:
            # Stack is empty
            serverConnectionFailure=False
            t=Timer(1,stackProcessingLoop)
            writeOutputs(datapoolclient.response)
        else:
            # Server answer missing
            serverConnectionFailure=True
            datapoolclient.addLog({'error':'Server connection failure, status polling turned off for the time being'})
            t=Timer(30.0,stackProcessingLoop)
    else:
        # Normal stack processing
        serverConnectionFailure=False
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
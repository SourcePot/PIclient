import datapoolclient
import os
import time
import pkgutil
from threading import Timer

sentinelStatus={'method':'piRequest','Content||activity':0,'Content||mode':'idle','Content||captureTime':3600,'Group':'Location','Folder':'Position','Name':'Pi entry'}
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
        leds['Content||alarm']=LED(17,initial_value=False)
        leds['Content||light']=LED(18,initial_value=False)
        leds['Content||motor']=LED(22,initial_value=False)
        leds['Content||direction']=LED(23,initial_value=False)
    strOutputs['console']='Client started'
    print(strOutputs['console'])
initOutputs()

def writeOutputs(response):
    global leds,strOutputs,sentinelStatus
    if type(response) is not bool:
        for key,value in response.items():
            if key in leds:
                if (int(value)>0):
                    leds[key].on()
                else:
                    leds[key].off()
            if key in strOutputs:
                if key=='console':
                    print(value)
            if key in sentinelStatus:
                # use a key-whitelist for status which should be updated by the server response
                if (key=='Content||captureTime' or  key=='Content||mode'):
                    sentinelStatus[key]=value

# ===================================== Sensors ===================================
def initInputs():
    global motionSensors
    if hasGpioZero:
        motionSensors['pirA']=MotionSensor(pin=27,pull_up=None,active_state=True)
        motionSensors['pirB']=MotionSensor(pin=24,pull_up=None,active_state=True)
initInputs()        

def readInputs():
    global leds
    inputs={}
    inputs['Date']=time.strftime('%Y-%m-%d %H:%M:%S',time.localtime())
    inputs['Content||timestamp']=int(time.time())
    for key,value in leds.items():
        inputs[key]=int(leds[key].is_active)
    if hasGpioZero:
        inputs['Content||cpuTemperature']=CPUTemperature().temperature
    return inputs

# ===================================== Behaviour =================================
activity=0

def captureFileNames(filename):
    global dirs
    frame=0
    while frame<4:
        yield dirs['media']+'/'+filename+'_'+str(int(time.time()))+'_'+str(frame)+'.jpg'
        frame+=1

busyCapturing=False
def capture(filename):
    global busyCapturing,sentinelStatus
    busyCapturing=True
    if hasPiCamera and sentinelStatus['Content||mode']!='idle':
        with picamera.PiCamera(framerate=2) as camera:
            camera.start_preview()
            time.sleep(1)
            camera.capture_sequence(captureFileNames(filename),use_video_port=True)
        mediaItems2stack()
    busyCapturing=False
 
def motionA():
    global busyCapturing,activity,sentinelStatus
    activity+=4
    if (busyCapturing==False):
        startStatus=readInputs()
        endStatus=startStatus
        if sentinelStatus['Content||mode']!='idle':
            startStatus['Content||light']=1
        if sentinelStatus['Content||mode']=='alarm':
            startStatus['Content||alarm']=1
        writeOutputs({'Content||light':startStatus['Content||light'],'Content||alarm':startStatus['Content||alarm']})
        capture('motionA')
        writeOutputs({'Content||light':endStatus['Content||light'],'Content||alarm':endStatus['Content||alarm']})
    
def motionB():
    global busyCapturing,activity
    activity+=1
    
if 'pirA' in motionSensors:
    motionSensors['pirA'].when_motion=motionA
if 'pirB' in motionSensors:
    motionSensors['pirB'].when_motion=motionB

def updateActivity():
    global sentinelStatus,activity
    sentinelStatus['Content||activity']=activity
    if (activity>0):
        activity-=1
    t=Timer(6,updateActivity)
    t.start()
updateActivity()

# ==== add media item and/or status data to stack and process the stack ===========

def mediaItems2stack():
    global dirs,sentinelStatus
    for file in os.listdir(dirs['media']):
        sentinelStatus=sentinelStatus|readInputs()
        sentinelStatus['Type']='piMedia'
        sentinelStatus['Name']=file
        fileNameComps=file.split('_')
        if (len(fileNameComps)==3):
            sentinelStatus['Content||timestamp']=fileNameComps[1]
        datapoolclient.add2stack(sentinelStatus,dirs['media']+'/'+file)
    
def statusPolling():
    global sentinelStatus
    sentinelStatus=sentinelStatus|readInputs()
    sentinelStatus['Type']='piStatus'
    datapoolclient.add2stack(sentinelStatus)
    t=Timer(4.7,statusPolling)
    t.start()
statusPolling()

def stackProcessingLoop():
    answer=datapoolclient.processStack()
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
        t=Timer(3.3,stackProcessingLoop)
    t.start()
stackProcessingLoop()

# ==== periodic capturing =========================================================
ticks=0
def periodicCapture():
    global ticks,sentinelStatus,busyCapturing
    captureTime=int(sentinelStatus['Content||captureTime'])
    if (captureTime!=0):
        if (ticks % captureTime==0):
            if (busyCapturing==False):
                capture('capture')
    ticks+=1
    t=Timer(1.0,periodicCapture)
    t.start()
periodicCapture()

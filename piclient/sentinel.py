import datapoolclient
import os
import time
import pathlib
import pkgutil
from threading import Timer

sentinelStatus={'method':'piRequest','Content||mode':'idle','Content||captureTime':10,'Group':'Town','Folder':'Street and Buildiung','Name':'Location'}
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
    inputs['Content||timeStamp']=int(time.time())
    for key in leds.items():
        inputs[key]=int(leds[key].is_active)
    if hasGpioZero:
        inputs['Content||cpuTemperature']=CPUTemperature().temperature
    return inputs

# ===================================== Behaviour =================================
def capture(filename):
    global dirs,leds
    if hasPiCamera:
        with picamera.PiCamera(framerate=1) as camera:
            camera.start_preview()
            time.sleep(1)
            camera.capture_sequence([
                dirs['media']+'/'+filename+'_%02d.jpg' % i
                for i in range(4)
                ],
            use_video_port=True)
            
def motionA():
    writeOutputs({'Content||light':1})
    capture(int(time.time())+'_motionA')
    writeOutputs({'Content||light':0})
    
def motionB():
    pass

if 'pirA' in motionSensors:
    motionSensors['pirA'].when_motion=motionA
if 'pirB' in motionSensors:
    motionSensors['pirB'].when_motion=motionB


# ==== add media item and/or status data to stack and process the stack ===========
mediaItems=[]
def getNextMediaItem():
    global dirs,mediaItems
    mediaItems=os.listdir(dirs['media'])
    if not mediaItems:
        return False
    else:
        mediaItems=sorted(mediaItems)
        return dirs['media']+'/'+mediaItems.pop(0)

def mediaItemPolling():
    global sentinelStatus
    mediaItem=getNextMediaItem()
    if type(mediaItem) is not bool:
        sentinelStatus=sentinelStatus|readInputs()
        datapoolclient.add2stack(sentinelStatus,mediaItem)
    t=Timer(0.9,mediaItemPolling)
    t.start()
mediaItemPolling()

def statusPolling():
    global sentinelStatus
    sentinelStatus=sentinelStatus|readInputs()
    datapoolclient.add2stack(sentinelStatus)
    t=Timer(4.3,statusPolling)
    t.start()
statusPolling()

def stackProcessingLoop():
    answer=datapoolclient.processStack()
    if type(answer) is bool:
        if answer==True:
            # Stack is empty
            t=Timer(0.3,stackProcessingLoop)
            writeOutputs(datapoolclient.response)
        else:
            # Server answer missing
            t=Timer(30.0,stackProcessingLoop)
    else:
        # Normal stck processing
        t=Timer(0.83,stackProcessingLoop)
    t.start()
stackProcessingLoop()
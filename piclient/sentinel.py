import datapoolclient
import os
import time
import pathlib
import pkgutil
from threading import Timer

sentinelStatus={'method':'piRequest','Content|[]|mode':'idle','Content|[]|captureTime':10,'Group':'Town','Folder':'Street and Buildiung','Name':'Location'}
motionSensors={}
leds={}
strOutputs={}

dirs=datapoolclient.getDirs()
print(dirs)

hasPiCamera=pkgutil.find_loader('picamera')
if hasPiCamera:
    import picamera

hasGpioZero=pkgutil.find_loader('gpiozero')
if hasGpioZero:
    from gpiozero import MotionSensor,CPUTemperature,LED

# ===================================== Outputs ==================================
def initOutputs():
    global leds
    if hasGpioZero:
        leds['Content|[]|alarm']=LED(17,initial_value=False)
        leds['Content|[]|light']=LED(18,initial_value=False)
        leds['Content|[]|motor']=LED(22,initial_value=False)
        leds['Content|[]|direction']=LED(23,initial_value=False)
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
    inputs['Content|[]|timeStamp']=int(time.time())
    for key,value in leds.items():
        inputs[key]=leds[key].is_active
    if hasGpioZero:
        inputs['Content|[]|cpuTemperature']=CPUTemperature().temperature
    return inputs

# ===================================== Behaviour =================================
def capture():
    global dirs,leds
    if hasPiCamera:
        with picamera.PiCamera(framerate=2) as camera:
                leds['Content|[]|light'].on()
                writeOutputs({'Content|[]|light':1})
                camera.start_preview()
                time.sleep(2)
                camera.capture_sequence([
                    dirs['media']+'/capture%02d.jpg' % i
                    for i in range(5)
                    ],
                use_video_port=True)
                writeOutputs({'Content|[]|light':0})

def motionA():
    capture()
    
def motionB():
    pass

if 'pirA' in motionSensors:
    motionSensors['pirA'].when_motion=motionA
if 'pirB' in motionSensors:
    motionSensors['pirB'].when_motion=motionB


# ============= Generic processing =========================================
mediaItems=[]
def getNextMediaItem():
    global dirs,mediaItems
    mediaItems=os.listdir(dirs['media'])
    if not mediaItems:
        return False
    else:
        mediaItems=sorted(mediaItems)
        return mediaItems.pop(0)

seconds=0
def polling():
    global dirs,sentinelStatus,seconds
    mediaItem=getNextMediaItem()
    sentinelStatus=sentinelStatus|readInputs()
    if type(mediaItem) is bool:
        response=datapoolclient.add2stack(sentinelStatus)
    else:
        mediaItem=dirs['media']+'/'+mediaItem
        response=datapoolclient.add2stack(sentinelStatus,mediaItem)
    #print(datapoolclient.response)
    writeOutputs(datapoolclient.response)
    seconds+=1
    t=Timer(1.0,polling)
    t.start()
polling()

def stackProcessingLoop():
    global datapoolResponse
    answer=datapoolclient.processStack()
    if type(answer) is bool:
        if answer==True:
            t=Timer(0.5,stackProcessingLoop)
        else:
            t=Timer(10.0,stackProcessingLoop)
    else:
        datapoolResponse=answer['response']
        t=Timer(0.5,stackProcessingLoop)
    t.start()
stackProcessingLoop()
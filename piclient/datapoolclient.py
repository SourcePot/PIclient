import os
import pathlib
import shutil
import codecs
import time
import requests
import json
import base64
from requests.auth import HTTPBasicAuth
from threading import Timer
from datetime import datetime

maxStackLength=10

#url='https://www.datapool.info/resource.php'
url='http://localhost/www-workspace/datapool/src/www/resource.php'

def jsonDecode(string):
    try:
        json_obj=json.loads(string)
    except ValueError as e:
        return True
    return json_obj

def initDirs():    
    dirs={'base':os.path.dirname(os.path.realpath(__file__))}
    #dirs={'base':os.getcwd()}
    dirs['settings']=dirs['base']+'/settings'
    if not os.path.isdir(dirs['settings']):
        os.mkdir(dirs['settings'],0o770)
    dirs['comstack']=dirs['base']+'/comstack'
    if not os.path.isdir(dirs['comstack']):
        os.mkdir(dirs['comstack'],0o770)
    dirs['logs']=dirs['base']+'/logs'
    if not os.path.isdir(dirs['logs']):
        os.mkdir(dirs['logs'],0o770)
    dirs['media']=dirs['base']+'/media'
    if not os.path.isdir(dirs['media']):
        os.mkdir(dirs['media'],0o770)
    return dirs;

dirs=initDirs()
accessFile=dirs['settings']+'/client.json'
tokenFile=dirs['settings']+'/token.json'

def getDirs():
    global dirs
    return dirs

def addLog(log={'Info':'Test log entry'}):
    global dirs
    newLine=''
    for key in log:
        newLine+=str(key)+": "+str(log[key])+","
    newLine=newLine.strip(", ")
    logFileContent=''
    now=datetime.now()
    logFileName=dirs['logs']+'/'+now.strftime("%Y-%m-%d %H")+' events.log'
    if os.path.isfile(logFileName):
        with open(logFileName) as f:
            logFileContent=f.read()
    logFileContent+=now.strftime("%d/%m/%Y %H:%M:%S")+'|'+newLine+"\n"
    with codecs.open(logFileName,"w","utf-8") as f:
        f.write(logFileContent)

def getAccess():
    global url
    global accessFile
    access={'client_app':'datapool-client','client_id':'pi','client_secret':'****','url':url}
    if os.path.isfile(accessFile):
        with open(accessFile) as f:
            fileContent=f.read()
            access=json.loads(fileContent)
    else:
        with codecs.open(accessFile,"w","utf-8") as f:
            json.dump(access,f)
    return access

def requestNewAccessToken(access):
    payload={'grant_type':'authorization_code','client_app':access['client_app']}
    resp={}
    try:
        # The datapool php-script might not be able to access the authorization header depending on the server settings of the datapool host
        """
        basic=HTTPBasicAuth(access['client_id'],access['client_secret'])
        resp=requests.post(access['url'],auth=basic,data=payload)
        """
        # This adds the authorization to the payload. This is needed if the php script can't recognize the authorization header
        encoded=(access['client_id']+':'+access['client_secret']).encode('ascii')
        payload['Authorization']='Basic '.encode('ascii')+base64.b64encode(encoded)
        resp=requests.post(access['url'],data=payload)
    except requests.exceptions.RequestException as e:
        return False
    return jsonDecode(resp.text)

def checkToken(token={}):
    initToken={'expires':0,'access_token':''}
    if type(token) is bool:
        return initToken
    elif "expires" in token:
        return token
    else:
        return initToken

def getAccessToken(access):
    global tokenFile
    token=checkToken()
    if os.path.isfile(tokenFile):
        with open(tokenFile,"r") as f:
            fileContent=f.read()
            token=checkToken(json.loads(fileContent))
    else:
        addLog({'info':'No token file found, will be created'})
    if int(token['expires'])<time.time():
        response=requestNewAccessToken(access)
        token=checkToken(response)
        with codecs.open(tokenFile,"w","utf-8") as f:
            json.dump(token,f)
            addLog({'info':'Tried to renew access token'})
    else:
        addLog({'info':'Valid access token found'})
    token['expires_in']=int(token['expires'])-time.time()
    return token

items=[]
itemsLength=0
def getNextItem():
    global dirs
    global items
    global itemsLength
    items=os.listdir(dirs['comstack'])
    if not items:
        return False
    else:
        items=[payload for payload in items if "payload" in payload]
        items=sorted(items)
        itemsLength=len(items)
        return items.pop(0)

def add2stack(payload={},attachmentFileName=''):
    global dirs
    global maxStackLength
    if itemsLength>maxStackLength:
        addLog({'warning':'Too many items, skipped add2stack'})
        return False
    id=str(time.time())
    id=id.replace('.','_')
    payloadFileName=dirs['comstack']+'/'+id+' payload.json'
    with codecs.open(payloadFileName,"w","utf-8") as payloadFile:
        if os.path.isfile(attachmentFileName):
            dataFileName=dirs['comstack']+'/'+id+' attachment.file'
            payload['fileName']=attachmentFileName
            payload['fileBasename']=os.path.basename(attachmentFileName)
            payload['fileReference']=dataFileName
            shutil.copyfile(attachmentFileName,dataFileName)
            os.remove(attachmentFileName)
        json.dump(payload,payloadFile)
    return payload

def clientRequest(payload):
    access=getAccess()
    token=getAccessToken(access)
    payload['Authorization']='Bearer '+token['access_token']
    hasDataFile=False
    if 'fileReference' in payload:
        dataFileName=payload['fileReference']
        dataFileBasename=payload['fileBasename']
        if os.path.isfile(dataFileName):
            hasDataFile=True
    try:
        if hasDataFile:
            files={'media':(dataFileBasename,open(dataFileName,'rb'))}
            resp=requests.post(access['url'],data=payload,files=files)
        else:
            resp=requests.post(access['url'],data=payload)
    except requests.exceptions.RequestException as e:
        return False
    return jsonDecode(resp.text)


response={}
def processStack():
    global dirs,response
    nextItem=getNextItem()
    if type(nextItem) is bool:
        result=True
        addLog({'info':'Stack is empty'})
    else:    
        result=False
        payloadFileName=dirs['comstack']+'/'+nextItem
        dataFileName=payloadFileName.replace('payload.json','attachment.file')
        with open(payloadFileName,'r') as payloadFile:
            payload=payloadFile.read()
            try:
                payload=json.loads(payload)
            except json.decoder.JSONDecodeError:
                print('Payload file json error: '+payload)
                payload={}
            response=clientRequest(payload)
            result=response
        if (type(response) is not bool) and os.path.isfile(payloadFileName):
            os.remove(payloadFileName)
            if os.path.isfile(dataFileName):
                os.remove(dataFileName)
            addLog({'success':'Processing stack, client request success','stack size':len(items)})
        else:
            addLog({'error':'Processing stack, client request failed will try later','stack size':len(items)})
    return result

# If this file is directly called (not imported) clientRequest will be called to test the client access
# Make sure you have the client registered within your Datapool web application and that you provide a method 
# which is valid within the Scope of the registered client.
if __name__=="__main__":
    print('This script should be imported, not called directly. Calling it directly runs this testcase...')
   
    payload={'method':'clientAccessTest','info':'For the client access test the token file will be send with the request'}
    #payload['response']=clientRequest(payload,tokenFile)   
    #payload['response']=add2stack(payload)
    #payload['response']=add2stack(payload,__file__)
    #payload['response']=add2stack(payload,tokenFile)
    #print(payload)
    print(processStack())
else:
    pass
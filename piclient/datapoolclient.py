import os
import shutil
import time
import requests
import json
import base64
from requests.auth import HTTPBasicAuth
from datetime import datetime
from threading import RLock

MAX_STACK_LENGTH=10
MAX_QUEUE_ITEM_AGE=30
LOGGING_ENABLED=False
# LOGGING_ENABLED=True

# URL='https://www.datapool.info/resource.php'
URL='https://www.wallenhauer.com/resource.php'
# URL='http://localhost/www-workspace/datapool/src/www/resource.php'
AUTHORIZATION_IN_HEADER=False

def jsonDecode(string):
    try:
        json_obj=json.loads(string)
    except ValueError as e:
        print(repr(e))
        return False
    return json_obj

dirs:dict[str,str]={}
def initDirs():
    global dirs
    dirs={'base':os.path.dirname(os.path.realpath(__file__))}
    #dirs={'base':os.getcwd()}
    dirs['settings']=dirs['base']+'/settings'
    if not os.path.isdir(dirs['settings']):
        os.mkdir(dirs['settings'],0o770)
    dirs['comstack']=dirs['base']+'/comstack'
    if not os.path.isdir(dirs['comstack']):
        os.mkdir(dirs['comstack'],0o770)
    dirs['comstack_failed']=dirs['base']+'/comstack_failed'
    if not os.path.isdir(dirs['comstack_failed']):
        os.mkdir(dirs['comstack_failed'],0o770)
    dirs['logs']=dirs['base']+'/logs'
    if not os.path.isdir(dirs['logs']):
        os.mkdir(dirs['logs'],0o770)
    dirs['media']=dirs['base']+'/media'
    if not os.path.isdir(dirs['media']):
        os.mkdir(dirs['media'],0o770)
initDirs()

accessFile=dirs['settings']+'/client.json'
tokenFile=dirs['settings']+'/token.json'

def getDirs():
    return dict(dirs)

def addLog(log={'Info':'Test log entry'}):
    if LOGGING_ENABLED:
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
        with open(logFileName,"w",encoding="utf-8") as f:
            f.write(logFileContent)

def getAccess():
    access={'client_id':'pi','client_secret':'****','url':URL}
    if os.path.isfile(accessFile):
        try:
            with open(accessFile,encoding="utf-8") as f:
                fileContent=f.read()
                access=json.loads(fileContent)
        except (OSError,json.JSONDecodeError) as e:
            addLog({'error':'Could not load client access configuration','exception':repr(e)})
            return None
    else:
        with open(accessFile,"w",encoding="utf-8") as f:
            json.dump(access,f,indent=2)
            f.write("\n")
    if not isinstance(access,dict) or not all(isinstance(access.get(key),str) and access[key] for key in ('client_id','client_secret','url')):
        addLog({'error':'Invalid client access configuration'})
        return None
    return access

def requestNewAccessToken(access):
    payload={'grant_type':'authorization_code'}
    try:
        requestOptions={}
        if AUTHORIZATION_IN_HEADER:
            requestOptions['auth']=HTTPBasicAuth(access['client_id'],access['client_secret'])
        else:
            encoded=(access['client_id']+':'+access['client_secret']).encode('ascii')
            payload['Authorization']='Basic '.encode('ascii')+base64.b64encode(encoded)
        resp=requests.post(access['url'],data=payload,timeout=30,**requestOptions)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(repr(e))
        return False
    return jsonDecode(resp.text)

def checkToken(token):
    if not isinstance(token,dict) or not isinstance(token.get('access_token'),str) or not token['access_token']:
        return None
    try:
        int(token['expires'])
    except (KeyError,TypeError,ValueError):
        return None
    return token

def getAccessToken(access):
    token=None
    if os.path.isfile(tokenFile):
        try:
            with open(tokenFile,"r") as f:
                fileContent=f.read()
                token=checkToken(json.loads(fileContent))
        except (OSError,json.JSONDecodeError) as e:
            addLog({'error':'Could not load access token','exception':repr(e)})
    else:
        addLog({'info':'No token file found, will be created'})
    if token is None or int(token['expires'])-int(time.time())-10<0:
        tokenRequestResponse=requestNewAccessToken(access)
        token=checkToken(tokenRequestResponse)
        if token is None:
            addLog({'error':'Could not obtain a valid access token'})
            return None
        with open(tokenFile,"w",encoding="utf-8") as f:
            json.dump(token,f)
            addLog({'info':'Tried to renew access token'})
    else:
        addLog({'info':'Valid access token found'})
    token['expires_in']=int(token['expires'])-time.time()
    return token

items=[]
stackLock=RLock()
def getNextItem():
    global items
    with stackLock:
        items=sorted(payload for payload in os.listdir(dirs['comstack']) if payload.endswith(' payload.json'))
        if not items:
            return False
        else:
            return items.pop(0)

def add2stack(payload=None,attachmentFileName=''):
    payloadData=dict(payload) if payload is not None else {}
    with stackLock:
        pendingPayloads=[name for name in os.listdir(dirs['comstack']) if name.endswith(' payload.json')]
        if len(pendingPayloads)>=MAX_STACK_LENGTH:
            addLog({'warning':'Too many items, skipped add2stack','stack size':len(pendingPayloads)})
            return False
        id=str(time.time()).replace('.','_')
        payloadFileName=dirs['comstack']+'/'+id+' payload.json'
        tempPayloadFileName=payloadFileName+'.tmp'
        dataFileName=''
        try:
            if os.path.isfile(attachmentFileName):
                dataFileName=dirs['comstack']+'/'+id+' attachment.file'
                payloadData['fileName']=attachmentFileName
                payloadData['fileBasename']=os.path.basename(attachmentFileName)
                payloadData['fileReference']=dataFileName
                shutil.copyfile(attachmentFileName,dataFileName)
            with open(tempPayloadFileName,"w",encoding="utf-8") as payloadFile:
                json.dump(payloadData,payloadFile)
            os.replace(tempPayloadFileName,payloadFileName)
            if dataFileName:
                os.remove(attachmentFileName)
        except Exception:
            if os.path.exists(tempPayloadFileName):
                os.remove(tempPayloadFileName)
            if dataFileName and os.path.exists(dataFileName) and not os.path.exists(payloadFileName):
                os.remove(dataFileName)
            raise
    return payloadData

def clientRequest(payload):
    access=getAccess()
    if access is None:
        return False
    token=getAccessToken(access)
    if token is None:
        return False
    requestOptions={}
    if AUTHORIZATION_IN_HEADER:
        requestOptions['headers']={'Authorization':'Bearer '+token['access_token']}
    else:
        payload['Authorization']='Bearer '+token['access_token']
    dataFileName=None
    dataFileBasename=None
    if 'fileReference' in payload:
        dataFileName=payload['fileReference']
        dataFileBasename=payload.get('fileBasename')
        if not isinstance(dataFileName,str) or not os.path.isfile(dataFileName) or not isinstance(dataFileBasename,str):
            addLog({'error':'Queued attachment is missing or invalid'})
            return False
    try:
        if dataFileName:
            with open(dataFileName,'rb') as attachment:
                resp=requests.post(access['url'],data=payload,files={'media':(dataFileBasename,attachment)},timeout=30,**requestOptions)
        else:
            resp=requests.post(access['url'],data=payload,timeout=30,**requestOptions)
        resp.raise_for_status()
    except requests.exceptions.RequestException as e:
        print(repr(e))
        return False
    except OSError as e:
        print(repr(e))
        return False
    responseData=jsonDecode(resp.text)
    if not isinstance(responseData,dict):
        addLog({'error':'Server returned an invalid response'})
        return False
    return responseData


response:dict[str,str]={}
def moveQueueItemToFailed(payloadFileName,reason):
    with stackLock:
        failedDir=dirs['comstack_failed']
        payloadBasename=os.path.basename(payloadFileName)
        suffix=' payload.json'
        if not payloadBasename.endswith(suffix):
            raise ValueError('Unexpected queue payload filename: '+payloadBasename)
        itemId=payloadBasename[:-len(suffix)]
        attachmentFileName=dirs['comstack']+'/'+itemId+' attachment.file'

        version=0
        while True:
            versionSuffix='' if version==0 else '_'+str(version)
            failedPayloadFileName=failedDir+'/'+itemId+versionSuffix+suffix
            failedAttachmentFileName=failedDir+'/'+itemId+versionSuffix+' attachment.file'
            if not os.path.exists(failedPayloadFileName) and not os.path.exists(failedAttachmentFileName):
                break
            version+=1

        movedAttachment=False
        try:
            if os.path.exists(attachmentFileName):
                os.replace(attachmentFileName,failedAttachmentFileName)
                movedAttachment=True
            os.replace(payloadFileName,failedPayloadFileName)
        except OSError:
            if movedAttachment:
                try:
                    os.replace(failedAttachmentFileName,attachmentFileName)
                except OSError as rollbackError:
                    print('Could not restore queue attachment: '+repr(rollbackError))
            raise

        print('Moved failed queue item to '+failedPayloadFileName+': '+reason)
        addLog({'error':'Moved queue item to failed directory','payload':failedPayloadFileName,'reason':reason})

def moveOrphanFileToFailed(fileName,reason):
    with stackLock:
        failedDir=dirs['comstack_failed']
        baseName,extension=os.path.splitext(fileName)
        version=0
        while True:
            versionSuffix='' if version==0 else '_'+str(version)
            failedFileName=failedDir+'/'+baseName+versionSuffix+extension
            if not os.path.lexists(failedFileName):
                break
            version+=1

        sourceFileName=dirs['comstack']+'/'+fileName
        os.replace(sourceFileName,failedFileName)
        print('Moved orphan queue file to '+failedFileName+': '+reason)
        addLog({'warning':'Moved orphan queue file to failed directory','file':failedFileName,'reason':reason})

def reportQueueRecoveryError(fileName,error):
    print('Could not recover queue file '+fileName+': '+repr(error))
    try:
        addLog({'error':'Could not recover queue file','file':fileName,'exception':repr(error)})
    except Exception as logError:
        print('Could not log queue recovery error: '+repr(logError))

def recoverQueueFiles():
    with stackLock:
        payloadSuffix=' payload.json'
        attachmentSuffix=' attachment.file'
        temporarySuffix=' payload.json.tmp'
        temporaryFilesToKeep=set()

        for name in os.listdir(dirs['comstack']):
            if not name.endswith(temporarySuffix):
                continue
            fileName=dirs['comstack']+'/'+name
            if not os.path.isfile(fileName):
                continue
            try:
                itemAge=time.time()-os.path.getmtime(fileName)
                if itemAge>MAX_QUEUE_ITEM_AGE:
                    moveOrphanFileToFailed(name,'Abandoned temporary payload file')
                else:
                    temporaryFilesToKeep.add(name)
            except Exception as e:
                reportQueueRecoveryError(name,e)
                temporaryFilesToKeep.add(name)

        payloadFiles=[
            name for name in os.listdir(dirs['comstack'])
            if name.endswith(payloadSuffix) and os.path.isfile(dirs['comstack']+'/'+name)
        ]
        now=time.time()
        for payloadName in payloadFiles:
            payloadFileName=dirs['comstack']+'/'+payloadName
            try:
                itemAge=now-os.path.getmtime(payloadFileName)
                if itemAge>MAX_QUEUE_ITEM_AGE:
                    moveQueueItemToFailed(payloadFileName,'Queue item exceeded maximum age')
            except Exception as e:
                reportQueueRecoveryError(payloadName,e)
                continue

        remainingFiles=os.listdir(dirs['comstack'])
        activePayloads={
            name for name in remainingFiles
            if name.endswith(payloadSuffix) and os.path.isfile(dirs['comstack']+'/'+name)
        }
        attachedFiles={
            name[:-len(payloadSuffix)]+attachmentSuffix
            for name in activePayloads
        }
        for name in remainingFiles:
            fileName=dirs['comstack']+'/'+name
            if name in activePayloads or name in attachedFiles or name in temporaryFilesToKeep:
                continue
            if os.path.isfile(fileName) or os.path.islink(fileName):
                try:
                    moveOrphanFileToFailed(name,'No active queue payload references this file')
                except Exception as e:
                    reportQueueRecoveryError(name,e)

def processStack():
    global response
    payloadFileName=None
    try:
        recoverQueueFiles()
        nextItem=getNextItem()
        if type(nextItem) is bool:
            addLog({'info':'Stack is empty'})
            return True

        payloadFileName=dirs['comstack']+'/'+nextItem
        dataFileName=payloadFileName.replace('payload.json','attachment.file')
        with open(payloadFileName,'r',encoding='utf-8') as payloadFile:
            payload=json.load(payloadFile)
        if not isinstance(payload,dict):
            raise ValueError('Queued payload must be a JSON object')

        result=clientRequest(payload)
        if type(result) is bool:
            addLog({'error':'Processing stack, client request failed will try later','stack size':len(items)})
            return result

        response=result
        if os.path.isfile(dataFileName):
            os.remove(dataFileName)
        if os.path.isfile(payloadFileName):
            os.remove(payloadFileName)
        addLog({'success':'Processing stack, client request success','stack size':len(items)})
        return result
    except Exception as e:
        print('Stack processing failed: '+repr(e))
        try:
            if payloadFileName is not None and os.path.exists(payloadFileName):
                moveQueueItemToFailed(payloadFileName,repr(e))
                response={}
                return response
            addLog({'error':'Stack processing exception','exception':repr(e)})
        except Exception as moveError:
            print('Could not move failed queue item: '+repr(moveError))
        return False

# If this file is directly called (not imported) clientRequest will be called to test the client access
# Make sure
# 	a) you have the client registered within your Datapool web application and
# 	b) you provide a method which is valid within the scope of the registered client.
if __name__=="__main__":
    print('This script should be imported, not called directly. Calling it directly runs this testcase...')
   
    testPayload={'method':'clientAccessTest','info':'For the client access test the token file will be send with the request'}
    #testPayload['response']=clientRequest(testPayload,tokenFile)   
    #testPayload['response']=add2stack(testPayload)
    #testPayload['response']=add2stack(testPayload,__file__)
    #testPayload['response']=add2stack(testPayload,tokenFile)
    #print(testPayload)
    print(processStack())
else:
    pass

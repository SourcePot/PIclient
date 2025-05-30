# Raspberry Pi Client
The Python code of this repository is for a Raspberry Pi. It enables the Raspberry Pi to connect to the Datapool web application.
It connects to the web application via the Datapool processor `SourcePot\Datapool\Processing\RemoteClient` and it can be used within any data app.

The typical application is a motion sensor triggered camera. Here are some examples:

![Raspberry Pi Client Mr Fox shot](/assets/img/mr_fox.jpg "Mr Fox")

![Repair and cleaning session](/assets/img/repair.jpg "Repair and cleaning session")

## How does it work?

The 'RemoteClient' class receives requests from e.g. multiple Raspberry Pis containing data (status information, sensory data) and/or files (images, videos). The web application's answer to each request contains the settings for the respective Raspberry Pi.

## First steps on the side of the Raspberry Pi
To setup the Raspberry Pi client you need to create a folder on your Raspberry Pi and copy the following three python files into this folder: 
1. \_\_init\_\_.py,
2. datapoolclient.py and 
3. sentinel.py

You will need to adjust the url in datapoolclient.py to the web address of __your__ Datapool web application:
![URL setting within datapoolclient.py](/assets/img/url.png "URL setting within datapoolclient.py")

When sentinel.py runs for the first time, datapoolclient.py will create a set of sub-directories. You will need to adjust the client.json file in the newly created settings sub-directory.

> [!IMPORTANT]  
> The `client.json` file contains the access details, such as the Datapool web application url, the client_id and client_secret.

These details must match the client registration within the Datapool web application.

![Update client.json with the correct client_id and client_secret](/assets/img/client-json.png "Content of client.json")

## Remote client registration within Datapool
You will need to register the new client with one of the Datapool user accounts. To do this, go to 'Admin' &rarr; 'Account' and expand 'App credentials' (Lock symbol).
Remember the registered client will have the same privileges as the user of this account but limited to the selected scope. The scope for the Raspberry Pi client must be class `SourcePot\Datapool\Processing\RemoteClient` and the method `clientCall`. The method clientCall of class SourcePot\Datapool\Processing\RemoteClient will handle the client requests.

The following screenshot shows the registration of the client in row 0001:

![Raspberry Pi client registration](/assets/img/datapool_client_registration.png "Client registration within the Datapool web application")

Multiple Raspberry Pis can run as clients with the same `client_id`. The Raspberry Pis are are distinguished by their location and the location of a Raspberry Pi is set by `entry={'Group':'Town','Folder':'Address','Name':'Location'}` in `sentinel.py`. Just replace Town, Address and Location with the correct values. 

When a Raspberry Pi connects for the very first time to the Datapool host a database entry is created based on Town, Address and Location in the Datapool database table `remotecliwent`. The entry's EntryId is `{baseEntryId}_definition` and contains the html widget template definitions for status and settings. These are provided by the Raspberry Pi, i.e. the Raspberry Pi's Python script defines the user interface within the Datapool web application. The settings, that control the Raspberry Pi, will be stored in the same table as entry with an EntryId="..._setting". The latest data provided by the Raspberry Pi is saved as entry in the same table with the EntryId=`{baseEntryId}_lastentry`.

![Client host communication](/assets/img/client-host-communication.png "Client host communication")

Initially the client needs to request a new access token. Aften having received the access token, the client can send client (status) data such as measurements, senosor data and optionally media files such as images or movies (POST request). The Datapool host answers the host request with new settings data for the client.

## Example view on the Datapool web application
The RemoteClient processor provides an user interface which is actually defined by the Python code of the remote client itself. Within the `sentinel.py` file the Python dictionary `entry`, key `Content||Settings||...` defines the control elements and `entry` key `Content||Status||...` the status elements (display). This allows each remote client to provide different functionalities and to specify its' specific control elements (buttons, drop-down menus, slider etc.) for the Datapool web application.

![Raspberry Pi client registration](/assets/img/remote-client.png "User Interface on a data app")
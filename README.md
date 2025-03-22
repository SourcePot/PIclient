# PI Client
The Python code of this repository is for a Raspberry Pi. It enables the Raspberry Pi to connect to the Datapool web application.
It connects to the web application via the data pool processor `SourcePot\Datapool\Processing\RemoteClient` and can be used within any data app.

'RemoteClient' receives requests from e.g. multiple Raspberry Pis containing data (status information, senosry data) and/or files (images, videos). The web application's answer to each request contains the settings for the respective Raspberry Pi.

## First steps on the side of the Raspberry Pi
To setup the Raspberry Pi client you need to create a folder on your PI and copy the following three python files into this folder: 
1. \_\_init\_\_.py,
2. datapoolclient.py and 
3. sentinel.py

You will need to adjust the url in datapoolclient.py to the web address of __your__ Datapool web application:
![URL setting within datapoolclient.py](/assets/img/url.png "URL setting within datapoolclient.py")

When you run sentinel.py for the first time datapoolclient.py will create a set of sub-directories.
You need to adjust the client.json file in the newly created settings sub-directory. This file contains the access details, such as the Datapool web application url, the client_id and client_secret.

![Update client.json with the correct client_id and client_secret](/assets/img/client-json.png "Content of client.json")

These details must match the client registration within the Datapool web application.

## First steps on the Datapool web application - Remote client registration
You need to register the new client with one of the user accounts of your web application. To do this go to 'Admin' &rarr; 'Account' and expand 'App credentials' (Lock symbol).
Remember the registered client will have the same privileges as the user of this account but limited to the selected scope. The scope for the PIclient must be class `SourcePot\Datapool\Processing\RemoteClient` and the method `clientCall`. Multiple Raspberry Pis can use the same `client_id`. The location of a PI is set by `entry={'Group':'Town','Folder':'Address','Name':'Location'}` in `sentinel.py`. The following screenshot shows the registration of the client in row 0001:

![Raspberry Pi client registration](/assets/img/datapool_client_registration.png "Client registration within the Datapool web application")

## Example view on the Datapool web application
The RemoteClient processor provides a user interface which is defined by the remote client. Within `sentinel.py` the python dictionary `entry`, key `Content||Settings||...` defines the control elements and key `Content||Status||...` the status display.

![Raspberry Pi client registration](/assets/img/remote-client.png "User Interface on a data app")




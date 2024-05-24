# PI Client
The Python code of this respository is for a Raspberry Pi. It enables the Raspberry Pi to connect to the Datapool web application.
Refer to the 'PI view' respository which is the corresponding web page (App) within the Datapool web application. 

'PI view' receives requests from multiple Raspberry Pis containing data and/or files.
The web application's answer to a request contains the return data for the corresponding Raspberry Pi.

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

## First steps on the side of Datapool web application
You need to register the new client with one of the user accounts of your web application. To do this go to 'Admin' &rarr; 'Account' an expand 'App credentials' (Lock symbol).
Remember the registered client will have the same privileges as a user of this account. Following screenshot shows the registration of the client in row 0001:
![Raspberry Pi client registration](/assets/img/datapool_client_registration.png "Client registration within the Datapool web application")




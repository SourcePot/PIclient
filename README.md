# PI Client
This is a Raspberry Pi client providing communication with a Datapool web application.
'PI view' (see other SourcePot repositories) is the corresponding web page within the Datapool web application. 

'PI view' can receive requests from multiple PIs containing data and/or files.
The web application's answer to a request contains the return data for the corresponding PI.
This means each communicating  PI keeps the connection alive.

## First steps on the side of the Raspberry Pi
To setup the Raspberry Pi client you need to create a folder on your PI and copy the following three python files into this folder: 
1. \_\_init\_\_.py,
2. datapoolclient.py and 
3. sentinel.py

You will need to adjust the url in datapoolclient.py to the web address of __your__ Datapool web application:
When you run sentinel.py for the first time datapoolclient.py will create set of sub-directories.
You need to adjust the client.json file in the newly created settings sub-directory. This file contains the access details, such as the Datapool web application url, the client_id and client_secret.
These details must match the client registration within the Datapool web application.
![Update client.json with the correct client_id and client_secret](/assets/img/client-json.png "Content of client.json")

## First steps on the side of Datapool webn application
On the side of the Datapool web application you need to register the new client with one of the user accounts of the web application.
The client will have the same privileges as a user of this account. Following figure shows the registration of the client, row 001:
![Raspberry Pi client registration](/assets/img/datapool_client_registration.png "Client registration within the Datapool web application")




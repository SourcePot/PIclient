# PI Client
This is a Raspberry Pi client providing communication with a Datapool web application.
'PI view' (see the other repositories) is the corresponding web page within the Datapool web application. The webpage can receive requests from multiple PIs containing data and files.
The web application answer to a request is used to send data back to the corresponding PI, i.e. the PI keeps the connection alive, not the web application.

## First steps
To setup the Raspberry Pi client you need to create a folder on your PI and copy the following three python files into this folder: 
1. \_\_init\_\_.py,
2. datapoolclient.py and 
3. sentinel.py

Additionally you will need to change the url in datapoolclient.py to the web address of __your__ Datapool web application and update the client.json file which will be created when you run sentinel.py for the first time.
![Update client.json with the correct client_id and client_secret](/assets/img/client-json.png "Content of client.json")

On the side of the Datapool web application you need to register the new client with one of the user accounts of the web application.
The client will have the same privileges as a user of this account. Following figure shows the registration of the client, row 001:
![Raspberry Pi client registration](/assets/img/datapool_client_registration.png "Client registration within the Datapool web application")




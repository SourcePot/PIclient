# PI Client
This is a Raspberry Pi client providing communication with a Datapool web application.
## First steps
To setup the Raspberry Pi client you need to create a folder on your PI and copy the following three python files into this folder: 
1. \_\_init\_\_.py,
2. datapoolclient.py and 
3. sentinel.py

Additionally you will need to change the url in datapoolclient.py to the web address of __your__ Datapool web application.

On the side of the Datapool web application you need to register the new client with one of the user accounts of the web application.
The client will have the priviledges of the user account. Following figure shows the registration of the client, row 001:
![Raspberry Pi client registration](/assets/img/datapool_client_registration.png "Invoice import")




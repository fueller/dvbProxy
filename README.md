tvhProxy
========

A small flask app to proxy requests between Plex Media Server and DVBLink Server.

#### tvhProxy configuration
1. In dvbProxy.py configure options as per your setup.
2. Create a virtual enviroment: ```$ virtualenv venv```
3. Activate the virtual enviroment: ```$ . venv/bin/activate```
4. Install the requirements: ```$ pip install -r requirements.txt```
5. Finally run the app with: ```$ python dvbProxy.py```

#### systemd service configuration
A startup script for Ubuntu can be found in dvbProxy.service (change paths in dvbProxy.service to your setup), install with:

    $ sudo cp dvbProxy.service /etc/systemd/system/dvbProxy.service
    $ sudo systemctl daemon-reload
    $ sudo systemctl enable dvbProxy.service
    $ sudo systemctl start dvbProxy.service

#### Plex configuration
Enter the IP of the host running dvbProxy including port 5004, eg.: ```192.168.1.50:5004```

svc
====

CMAC web services

Install Dependencies via pip
----------------------------
source activate
pip install flask
pip install gunicorn
pip install tornado
pip install httplib2
pip install lxml

Need to have installed:
octave
epd python
ferret
GNU plot Version 4.6 patchlevel 4

To install/develop
--------------------------
python setup.py develop|install

To run in development mode
--------------------------
python run.py

To run in production mode
--------------------------
gunicorn -w2 -b 0.0.0.0:8888 -k tornado --daemon -p svc.pid svc:app

To deploy, first edit these three files:
host.cfg
settings.cfg
data.cfg
to set the hostname, port #, and data dir right.

Then go to 
../../web_portal/cmac/web
and edit all html files
to set the port right.

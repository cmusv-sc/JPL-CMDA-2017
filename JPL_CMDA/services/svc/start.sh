#!/bin/bash
/home/svc/anaconda2/bin/gunicorn -w6 --timeout 300 --graceful-timeout 600 -b 0.0.0.0:8890 -k tornado --daemon -p svc.pid svc:app
#/home/svc/install/bin/gunicorn -w6 --timeout 300 --graceful-timeout 600 -b 0.0.0.0:8890 -k tornado --daemon -p svc.pid svc:app
#/home/svc/install/epd/bin/gunicorn  -w6 --timeout 300 --graceful-timeout 600 -b 0.0.0.0:8890 -k tornado --daemon -p svc.pid svc:app

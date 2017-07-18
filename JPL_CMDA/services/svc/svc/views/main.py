from flask import render_template

from svc import app

@app.route('/')
def index():
    #app.logger.debug("Got here")
    return render_template('index.html', title="svc",
                           content="CMAC web services")

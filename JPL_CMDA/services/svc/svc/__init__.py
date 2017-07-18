from flask import Flask

app = Flask(__name__)
app.config.from_pyfile('../settings.cfg')

import svc.services
import svc.views
import svc.src

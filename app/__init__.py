# -*- coding: utf-8 -*-

import os

from config import Config

from flask import Flask
from flask_mail import Mail
from flask_moment import Moment
from flask_sslify import SSLify
from flask_login import LoginManager
from flask_bootstrap import Bootstrap
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow

app = Flask(__name__)
app.config.from_object(Config)

bootstrap = Bootstrap(app)
login = LoginManager(app)
login.login_view = 'login'
moment = Moment(app)
mail = Mail(app)
db = SQLAlchemy(app)
ma = Marshmallow(app)

from app import routes, models, errors

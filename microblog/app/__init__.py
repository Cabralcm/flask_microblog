import logging
from logging.handlers import SMTPHandler, RotatingFileHandler #Email Server

import os

from flask import Flask
from config import Config
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate
from flask_login import LoginManager

# Flask App Setup
app = Flask(__name__)
app.config.from_object(Config)

#  Database
db = SQLAlchemy(app)
migrate = Migrate(app, db)

# Login
login = LoginManager(app)
login.login_view = 'login' #The view function under routes.py that handles logins. The name you would use in a url_for()

from app import routes, models, errors

if not app.debug:

    if not os.path.exists('logs'):
        os.mkdir('logs')
    file_handler = RotatingFileHandler('logs/microblog.log', maxBytes=10240, backupCount=10)
    file_handler.setFormatter(logging.Formatter(
        '%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]'))
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)

    app.logger.setLevel(logging.INFO)
    app.logger.info('Microblog startup')

    if app.config['MAIL_SERVER']:
        
        auth = None
        if app.config['MAIL_USERNAME'] or app.config['MAIL_PASSWORD']:
            auth = (app.config['MAIL_USERNAME'], app.config['MAIL_PASSWORD'])
        
        secure = None
        if app.config['MAIL_USE_TLS']:
            secure = ()
        
        mail_handler = SMTPHandler(
            mailhost = (app.config['MAIL_SERVER'], app.config['MAIL_PORT']),
            fromaddr='no-reply@' + app.config['MAIL_SERVER'],
            toaddrs = app.config['ADMINS'], 
            subject='Microblog Failure',
            credentials=auth,
            secure=secure
        )
        mail_handler.setLevel(logging.ERROR)
        app.logger.addHandler(mail_handler)
# -*- coding: utf-8 -*-

import os


from datetime import timedelta


basedir = os.path.abspath(os.path.dirname(__file__))
appdir = os.path.join(basedir, 'app')
tempdir = os.path.join(appdir, 'tempfiles')

temlates_folder = os.path.join(appdir, 'templates')

taxi_folder = os.path.join(appdir, 'taxifiles')
taxi_approval_folder = os.path.join(taxi_folder, 'approvals')


class Config(object):

    FLASK_ENV = os.environ.get('FLASK_ENV') or 'prodaction'
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'my-super-secret-key'
    
    SESSION_COOKIE_NAME = 'servsession'
    SESSION_COOKIE_SECURE = True
    SESSION_COOKIE_HTTPONLY = True
    SESSION_REFRESH_EACH_REQUEST = True


    PYTHONIOENCODING = 'UTF-8'
    
    UPLOAD_FOLDER = tempdir
    TEMPLATES_FOLDER = temlates_folder
    SURVEYS_FOLDER = survey_folder
    PERMANENT_SESSION_LIFETIME = timedelta(hours=4)

    # AD settings
    AD_PORT = os.environ.get('AD_PORT')
    AD_SERVER = os.environ.get('AD_SERVER')
    AD_HOST = os.environ.get('AD_HOST')
    AD_SEARCH_TREE = os.environ.get('AD_SEARCH_TREE')
    AD_CONN_TIMEOUT = 3

    # MySQL DB settings
    DB_USER = os.environ.get('DB_USER')
    DB_PASSWORD = os.environ.get('DB_PASSWORD')
    DB_HOST = os.environ.get('DB_HOST')
    DB_PORT = os.environ.get('DB_PORT')
    DB_NAME = os.environ.get('DB_NAME')
    DB_TAXI_NAME = os.environ.get('DB_TAXI_NAME')
    DB_SURVEYS_NAME = os.environ.get('DB_SURVEYS_NAME')
    DB_EMPLOYEE_NAME = os.environ.get('DB_EMPLOYEE_NAME')
    DB_HELPDESK_NAME = os.environ.get('DB_HELPDESK_NAME')
    MAX_CONTENT_LENGTH = 20 * 1024 * 1024

    # SQLALCHEMY DB settings
    SQLALCHEMY_TRACK_MODIFICATIONS =  True
    SQLALCHEMY_DATABASE_URI = 'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME)

    SQLALCHEMY_BINDS = {
        'helpdesk':'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_HELPDESK_NAME),
        'surveys':'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_SURVEYS_NAME),
        'taxi':'mysql+mysqlconnector://{0}:{1}@{2}:{3}/{4}'.format(DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_TAXI_NAME)
        }
    
    # KNOX Email settings
    MAIL_SERVER = os.environ.get('MAIL_SERVER')
    MAIL_PORT = int(os.environ.get('MAIL_PORT')
    MAIL_USE_TLS = os.environ.get('MAIL_USE_TLS') is not None
    MAIL_USERNAME = os.environ.get('MAIL_USERNAME')
    MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD')
    
    MAIL_DEFAULT_SENDER = os.environ.get('MAIL_DEFAULT_SENDER')
    ADMINS = []

    # Approval files extensions
    IMAGE_EXTENSIONS = set(['png', 'jpg', 'jpeg', 'gif'])
    ALLOWED_EXTENSIONS = set(['pdf', 'png', 'jpg', 'jpeg', 'gif', 'eml',
                              'mht', 'msg', 'xls', 'xlsx', 'doc', 'docx',
                              'ppt', 'pptx', 'mp4', 'avi', 'txt', 'xml', 
                              'csv'])
    TAXI_APPROVALS_FOLDER = taxi_approval_folder

    


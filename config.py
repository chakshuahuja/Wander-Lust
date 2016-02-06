import os

basedir = os.path.abspath(os.path.dirname(__file__))
SQLALCHEMY_DATABASE_URI = 'sqlite:///'+os.path.join(basedir,'accounts.db')
SECRET_KEY = os.urandom(24)
WTF_CSRF_ENABLED = True
UPLOAD_FOLDER = basedir + '/Uploads/'
print UPLOAD_FOLDER

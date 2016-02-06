from config import SQLALCHEMY_DATABASE_URI
from app import app,db

db.create_all()

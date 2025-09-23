from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()

def init_db(app):
    
    db.init_app(app)
    
    return db

class Base(DeclarativeBase):
    pass

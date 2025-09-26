from flask_sqlalchemy_lite import SQLAlchemy
from sqlalchemy.orm import DeclarativeBase

db = SQLAlchemy()

def init_db(app):
    
    db.init_app(app)
    
    return db

class Base(DeclarativeBase):
    pass

def reset_db():
    from src.core.issue import Issue #noqa: F401

    print("Resetting database...")
    Base.metadata.drop_all(bind=db.engine)
    Base.metadata.create_all(bind=db.engine)
    print("Database reset complete.")


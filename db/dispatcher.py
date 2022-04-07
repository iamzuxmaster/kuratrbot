from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import os
from pathlib import Path


DB = 'db.sqlite3' 

Base = declarative_base()

BASE_DIR = Path(__file__).resolve().parent.parent


connection_string = "sqlite:///"+os.path.join(BASE_DIR, DB)
print(connection_string)
engine = create_engine(connection_string)
Session = sessionmaker()

def get_or_create(session, model, **kwargs):
    instance = session.query(model).filter_by(**kwargs).first()
    if instance:
        return instance, False
    else:
        instance = model(**kwargs)
        session.add(instance)
        session.commit()
        return instance, True

def object_get(session, model, **kwargs):
    try:
        instance = session.query(model).filter_by(**kwargs).first()
    except:
        instance = None
    return instance

def object_delete(session, model, **kwargs):
    try:
        instance = session.query(model).filter_by(**kwargs).delete()
    except:
        instance = None
    return instance


def object_create(session, model, **kwargs):
    instance = model(**kwargs)
    session.add(instance)
    session.commit()
    return instance

    
def objects_all(session, model):    
    instance = session.query(model).all()
    return instance

def objects_filter(session, model, **kwargs):
    try:
        instance = session.query(model).filter_by(**kwargs)
    except:
        instance = None
    return instance

# def create_db():
#     Base.metadata.create_all(engine)
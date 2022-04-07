from sqlalchemy import Column, String, DateTime, Integer, Boolean,ForeignKey
from datetime import datetime
from .dispatcher import Base, Session, engine

session_db = Session(bind=engine)

class Admin(Base): 
    __tablename__ = "admin"
    id = Column(Integer(), primary_key=True)
    telegram_id = Column(String(80), nullable=False)
    fullname=  Column(String(80), nullable=True)
    phone = Column(Integer(), nullable=True)
    date_created = Column(DateTime(), default=datetime.utcnow)


class Groups(Base): 
    __tablename__ = 'Groups'
    id = Column(Integer(), primary_key=True)
    telegram_id = Column(String(), nullable=True)
    title = Column(String(80), nullable=False, unique=True)
    date_created = Column(DateTime(), nullable=True, default=datetime.utcnow)


class User(Base): 
    __tablename__ = 'Users'
    id = Column(Integer(), primary_key=True)
    telegram_id = Column(String(80), nullable=False)
    telegram_name = Column(String(80), nullable=True)
    lang = Column(String(5), server_default="uz")
    fullname=  Column(String(80), nullable=True)
    username = Column(String(80))
    phone = Column(Integer())
    request_group = Column(String(80))
    verified = Column(Boolean(), default=False)
    group_id = Column(Integer(), ForeignKey('Groups.id'), nullable=True)
    date_created = Column(DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"< User: {self.fullname}, ID: {self.telegram_id}/>"




class Messages(Base): 
    __tablename__ = "Messages"
    id = Column(Integer(), primary_key=True)
    from_admin = Column(Integer(), ForeignKey('admin.id'))
    all = Column(Boolean(), nullable=True)
    title = Column(String(80), nullable=False)
    description = Column(String(300), nullable=True)
    date_created  = Column(DateTime(), default=datetime.utcnow)

    def __repr__(self):
        return f"<Messages: {self.title}, date: {self.date_created}"

# model tabeli Users
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean
from db.db_connect import Base

class User(Base):
    __tablename__ = "users"
    ID = Column(Integer, primary_key=True)
    Username = Column(String)
    Email = Column(String)
    Password = Column(String)
    Role = Column(String)
    
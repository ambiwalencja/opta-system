# model tabeli Users
from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, MetaData, relationship, ForeignKey
from db.db_connect import rebase
from sqlalchemy.ext.declarative import declarative_base

UserDataBase = declarative_base(metadata=MetaData(schema="UserData"))
# user_metadata = MetaData(schema='UserData')
# UserDataBase = declarative_base(metadata=user_metadata)

@rebase
class User(UserDataBase):
    __tablename__ = "user"
    ID_uzytkownika = Column(Integer, primary_key=True)
    Username = Column(String)
    Email = Column(String)
    Password = Column(String)
    Role = Column(String)

    pacjenci = relationship("Pacjent", back_populates="uzytkownik")
    wizyty_indywidualne = relationship('WizytyIndywidualne', back_populates="uzytkownik")
    grupy = relationship('Grupa', back_populates='uzytkownik')
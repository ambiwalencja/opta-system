from sqlalchemy import Column, Integer, String, DateTime
# from sqlalchemy import MetaData
# from db.db_connect import rebase
# from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from db.db_connect import Base

print(id(Base))

# UserDataBase = declarative_base(metadata=MetaData(schema="user_data"))
# user_metadata = MetaData(schema='UserData')
# UserDataBase = declarative_base(metadata=user_metadata)

# @rebase
class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_data"}
    ID_uzytkownika = Column(Integer, primary_key=True)
    Created = Column(DateTime)
    Last_modified = Column(DateTime)
    Username = Column(String)
    Email = Column(String)
    Password = Column(String)
    Role = Column(String)

    pacjenci = relationship("Pacjent", back_populates="uzytkownik")
    wizyty_indywidualne = relationship('WizytaIndywidualna', back_populates="uzytkownik")
    grupy = relationship('Grupa', back_populates='uzytkownik')
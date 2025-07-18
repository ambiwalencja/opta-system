from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import relationship
from db.db_connect import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_data"}
    ID_uzytkownika = Column(Integer, primary_key=True)
    Created = Column(DateTime)
    Last_modified = Column(DateTime)
    Last_login = Column(DateTime) # nullable musi być - wygląda na to, że na razie może pozostać tak jak jest, bo trzeba byłoby raczej ustawić nullable=false, chyba domyslnie jest nullable=true
    Username = Column(String)
    Password = Column(String)
    Role = Column(String)

    pacjenci = relationship("Pacjent", back_populates="uzytkownik")
    wizyty_indywidualne = relationship('WizytaIndywidualna', back_populates="uzytkownik")
    grupy = relationship('Grupa', back_populates='uzytkownik')
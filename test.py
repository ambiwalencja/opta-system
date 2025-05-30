from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from db.db_connect import Base


class Pacjent(Base):
    __tablename__ = "pacjenci" 
    __table_args__ = {'schema': 'client_data'}
    ID_pacjenta = Column(Integer, primary_key=True)
    ID_uzytkownika = Column(Integer, ForeignKey('user_data.users.ID_uzytkownika'))
    Timestamp = Column(DateTime)
    Data_zgloszenia = Column(Date)
    Imie = Column(String)
    Nazwisko = Column(String)
    Email = Column(String) 
    Telefon = Column(String)
    Dzielnica = Column(String)
    Ulica = Column(String)
    Nr_domu = Column(Integer)
    Nr_mieszkania = Column(Integer)
    Kod_pocztowy = Column(String)

    wizyty_indywidualne = relationship("WizytaIndywidualna", back_populates='pacjent')
    uzytkownik = relationship("User", back_populates="pacjenci")
    uczestnik_grupy = relationship('UczestnikGrupy', back_populates='pacjent')


class WizytaIndywidualna(Base):
    __tablename__ = "wizyty_indywidualne"
    __table_args__ = {'schema': 'client_data'}
    ID_wizyty = Column(Integer, primary_key=True)
    ID_pacjenta = Column(Integer, ForeignKey('pacjenci.ID_pacjenta')) 
    ID_uzytkownika = Column(Integer, ForeignKey('user_data.users.ID_uzytkownika'))
    Timestamp = Column(DateTime)
    Data = Column(Date) 
    Specjalista = Column(String)
    Notatka_opis_sytuacji = Column(String)

    pacjent = relationship('Pacjent', back_populates='wizyty_indywidualne')
    uzytkownik = relationship('User', back_populates='wizyty_indywidualne')


class Grupa(Base):
    __tablename__ = "grupy"
    __table_args__ = {'schema': 'client_data'}
    ID_grupy = Column(Integer, primary_key=True)
    ID_uzytkownika = Column(Integer, ForeignKey('user_data.users.ID_uzytkownika'))
    Nazwa_grupy = Column(String)
    Timestamp = Column(DateTime)
    Typ_grupy = Column(String) 

    spotkania_grupowe = relationship('Spotkanie_grupowe', back_populates='grupa')
    uzytkownik = relationship('User', back_populates='grupy')

class Spotkanie_grupowe(Base):
    __tablename__ = "spotkania_grupowe"
    __table_args__ = {'schema': 'client_data'}
    ID_spotkania = Column(Integer, primary_key=True)
    ID_grupy = Column(Integer, ForeignKey('grupy.ID_grupy'))
    Timestamp = Column(DateTime)
    Data = Column(Date)
    Prowadzacy = Column(String) 
    Notatka_rezultaty = Column(String)

    grupa = relationship('Grupa', back_populates='spotkania_grupowe')
    uczestnik_grupy = relationship('UczestnikGrupy', back_populates='grupa')

class UczestnikGrupy(Base):
    __tablename__ = "uczestnicy_grupy"
    __table_args__ = {'schema': 'client_data'}
    ID_uczestnika_grupy = Column(Integer, primary_key=True) 
    ID_grupy = Column(Integer, ForeignKey('grupy.ID_grupy'))
    ID_pacjenta = Column(Integer, ForeignKey('pacjenci.ID_pacjenta'))
    Ukonczenie = Column(Boolean)
    Rezultat = Column(Boolean)

    grupa = relationship('Grupa', back_populates='uczestnik_grupy')
    pacjent = relationship('Pacjent', back_populates='uczestnik_grupy')


from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship
from db.db_connect import Base


class User(Base):
    __tablename__ = "users"
    __table_args__ = {"schema": "user_data"}
    ID_uzytkownika = Column(Integer, primary_key=True)
    Username = Column(String)
    Email = Column(String)
    Password = Column(String)
    Role = Column(String)

    pacjenci = relationship("Pacjent", back_populates="uzytkownik")
    wizyty_indywidualne = relationship('WizytaIndywidualna', back_populates="uzytkownik")
    grupy = relationship('Grupa', back_populates='uzytkownik')
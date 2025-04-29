# Model tabeli Execution
from sqlalchemy import Column, Integer, String, DateTime, Date # Lista
from db.db_connect import Base

class Spotkanie_grupowe(Base):
    __tablename__ = "spotkania_grupowe" # to musi być dokładnie ta sama nazwa, co nazwa tabeli, do której chcemy wrzucać dane
    ID_spotkania = Column(Integer, primary_key=True)
    ID_grupy = Column(Integer) # foreign key
    Timestamp = Column(DateTime)
    Data = Column(Date)
    Prowadzacy = Column(String) # ?
    Liczba_godzin = Column(Integer)
    Obecni_uczestnicy = Column(Integer) # lista ID pacjentow
    Notatka_przebieg = Column(String)
    Notatka_rezultaty = Column(String)
    # pytanie - jak zapisywać rezultaty indywidualne - potrzebny wpis w bazie wizyt indywidualnych ?


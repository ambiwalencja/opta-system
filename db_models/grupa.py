from sqlalchemy import Column, Integer, String, DateTime, Date
from db.db_connect import Base

class Grupa(Base):
    __tablename__ = "grupy" # to musi być dokładnie ta sama nazwa, co nazwa tabeli, do której chcemy wrzucać dane
    ID_grupy = Column(Integer, primary_key=True)
    Nazwa_grupy = Column(String)
    Timestamp = Column(DateTime) # data dodania?
    Data_rozpoczecia = Column(Date) # ? czy to będzie po prostu data pierwszego spotkania
    Data_zakonczenia = Column(Date) # ? jw - data ostatniego
    Prowadzacy = Column(String) # Lista ID uzytkownikow
    Liczba_godzin = Column(Integer) # czy potrzebne? to może być suma czasu trwania poszczególnych spotkań
    Typ_grupy = Column(String) # warsztat, czy grupa wsparcia, czy trening, etc



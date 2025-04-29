# Model tabeli Execution
from sqlalchemy import Column, Integer, String, DateTime, Date
from db.db_connect import Base

class Wizyta(Base):
    __tablename__ = "wizyty" # to musi być dokładnie ta sama nazwa, co nazwa tabeli, do której chcemy wrzucać dane
    ID_wizyty = Column(Integer, primary_key=True)
    ID_pacjenta = Column(Integer) # foreign key
    Timestamp = Column(DateTime)
    Data = Column(Date) # z tego można wziąć rok, miesiąc
    Specjalista = Column(String) # albo Column(Int) ale moim zdaniem lepiej opisowo
    Liczba_godzin = Column(Integer) # czy potrzebne?
    Notatka_diagnoza_sytuacji = Column(String) # do decyzji czy tutaj czy przy pacjencie
    Notatka_opis_sytuacji = Column(String)
    Notatka_indywidualny_plan = Column(String)
    Notatka_rezultaty = Column(String)
    Notatka_odeslanie_do_innych = Column(String)


from sqlalchemy import Column, Integer, Boolean
from db.db_connect import Base

class UczestnikGrupy(Base):
    __tablename__ = "uczestnik_grupy"
    ID_uczestnika_grupy = Column(Integer, primary_key=True) # id pary - uczestniko-grupy
    ID_grupy = Column(Integer) # foreign key
    ID_pacjenta = Column(Integer) # foreign key
    Ukonczenie = Column(Boolean)
    Rezultat = Column(Boolean)
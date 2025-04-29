# tabela pomocnicza - possible values

from sqlalchemy import Column, Integer, String, JSON
from db.db_connect import Base

class PossibleValues(Base):
    __tablename__ = "possible_values"
    Variable_ID = Column(Integer, primary_key=True)
    Variable_name = Column(String)
    Variable_label = Column(String)
    Possible_values = Column(JSON)



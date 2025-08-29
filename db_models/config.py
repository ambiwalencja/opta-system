from sqlalchemy import Column, Integer, String, JSON, DateTime
from db.db_connect import Base

class PossibleValues(Base):
    __tablename__ = "possible_values"
    __table_args__ = {'schema': 'config'}
    Last_modified = Column(DateTime)
    Variable_ID = Column(Integer, primary_key=True)
    Variable_name = Column(String)
    Variable_label = Column(String)
    Possible_values = Column(JSON)
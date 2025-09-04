from sqlalchemy import Column, Integer, String, DateTime # , JSON
from sqlalchemy.dialects.postgresql import JSON
from db.db_connect import Base
from datetime import datetime
import json

class PossibleValues(Base):
    __tablename__ = "possible_values"
    __table_args__ = {'schema': 'config'}
    Last_modified = Column(DateTime)
    # # i jeszcze to do sprawdzenia TODO 3 - zamiast w insercie
    # Last_modified = Column(
    #     DateTime, 
    #     default=datetime.now,       # sets timestamp on insert
    #     onupdate=datetime.now       # updates timestamp automatically on update
    #     )
    Variable_ID = Column(Integer, primary_key=True)
    Variable_name = Column(String)
    Variable_label = Column(String)
    Possible_values = Column(JSON)
from sqlalchemy import Column, Integer, String, JSON, DateTime
# from sqlalchemy import MetaData
# from sqlalchemy.ext.declarative import declarative_base
from db.db_connect import Base

# if __name__ == "__main__":

# ConfigBase = declarative_base(metadata=MetaData(schema="config"))
# config_metadata = MetaData(schema='Config')
# ConfigBase = declarative_base(metadata=config_metadata)

print(id(Base))

class PossibleValues(Base):
    __tablename__ = "possible_values"
    __table_args__ = {'schema': 'config'}
    Last_modified = Column(DateTime)
    Variable_ID = Column(Integer, primary_key=True)
    Variable_name = Column(String)
    Variable_label = Column(String)
    Possible_values = Column(JSON)
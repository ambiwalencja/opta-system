from sqlalchemy import Column, Integer, String, JSON, MetaData
from sqlalchemy.ext.declarative import declarative_base

if __name__ == "__main__":
    ConfigBase = declarative_base(metadata=MetaData(schema="config"))
    # config_metadata = MetaData(schema='Config')
    # ConfigBase = declarative_base(metadata=config_metadata)


    class PossibleValues(ConfigBase):
        __tablename__ = "possible_values"
        Variable_ID = Column(Integer, primary_key=True)
        Variable_name = Column(String)
        Variable_label = Column(String)
        Possible_values = Column(JSON)
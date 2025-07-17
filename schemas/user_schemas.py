from pydantic import BaseModel
from pydantic.fields import Field
# from typing import List


class UserBase(BaseModel):
    username: str
    password: str
    role: str


class UserDisplay(BaseModel):
    username: str = Field(alias='Username', serialization_alias='username')
    role: str = Field(alias='Role', serialization_alias='role')
    class Config(): # to robi, że klasa UserDisplay rozumie, czyta obiekty sqlalchemy i jest w stanie zmapować na jsona
        from_attributes = True


class UserSignIn(BaseModel):
    username: str
    password: str
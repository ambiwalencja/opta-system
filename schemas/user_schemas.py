from pydantic import BaseModel
from pydantic.fields import Field
# from typing import List


class UserBase(BaseModel):
    username: str
    password: str
    role: str


class UserDisplay(BaseModel):
    username: str = Field(alias='Username')
    role: str = Field(alias='Role') # TODO: czy tutaj chodziło o to, żeby sie rozumieć z bazą danych? bo w bazie te atrybuty są z wielkiej litery właśnie.
    class Config(): # to robi, że klasa UserDisplay rozumie, czyta obiekty sqlalchemy i jest w stanie zmapować na jsona
        from_attributes = True


class UserSignIn(BaseModel):
    username: str
    password: str
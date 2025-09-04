from pydantic import BaseModel
from pydantic.fields import Field
from enum import Enum

class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"
 
class UserBase(BaseModel):
    full_name: str
    username: str
    password: str
    role: RoleEnum
    status: StatusEnum = "active"  # default value
    specjalista: list[str] # values in possible_values
    # Enum validation - hardcoded, for values that don't change
    # possible_values validation - for values that can be changed by user

    # TODO: tutaj taka propozycja od AI - może warto sprawdzić sposób walidacji taki
    # @model_validator(mode='after')
    # def validate_specjalista(self):
    #     from utils.validation import validate_choice
    #     for spec in self.specjalista:
    #         validate_choice(db, "Specjalista", spec)
    #     return self

class UserDisplay(BaseModel):
    full_name: str = Field(alias='Full_name', serialization_alias='full_name')
    username: str = Field(alias='Username', serialization_alias='username')
    role: str = Field(alias='Role', serialization_alias='role')
    specjalista: list[str] = Field(alias='Specjalista', serialization_alias='specjalista')
    status: str = Field(alias='Status', serialization_alias='status')
    class Config(): 
        from_attributes = True # to robi, że klasa UserDisplay rozumie, czyta obiekty sqlalchemy i jest w stanie zmapować na jsona
        # bez tego trzeba byłoby podawać dane w postaci dicta, jsona, a tak można 


class UserSignIn(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    refresh_token: str

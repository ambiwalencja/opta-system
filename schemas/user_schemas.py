from pydantic import BaseModel
from pydantic.fields import Field
from enum import Enum
from typing import Optional, List


class RoleEnum(str, Enum):
    user = "user"
    admin = "admin"

class StatusEnum(str, Enum):
    active = "active"
    inactive = "inactive"

class UserBase(BaseModel):
    """Base user schema with common fields and configuration"""
    full_name: str = Field(alias='Full_name', serialization_alias='full_name')
    username: str = Field(alias='Username', serialization_alias='username')
    role: RoleEnum = Field(alias='Role', serialization_alias='role')
    specjalista: List[str] = Field(alias='Specjalista', serialization_alias='specjalista')
    status: StatusEnum = Field(
        alias='Status',
        serialization_alias='status',
        default=StatusEnum.active
    ) # values in possible_values
    # Enum validation - hardcoded, for values that don't change
    # possible_values validation - for values that can be changed by user
    class Config:
        populate_by_name = True

class UserCreate(UserBase):
    """Schema for user creation"""
    password: str = Field(alias='Password', serialization_alias='password')

    # TODO: tutaj taka propozycja od AI - może warto sprawdzić sposób walidacji taki
    # @model_validator(mode='after')
    # def validate_specjalista(self):
    #     from utils.validation import validate_choice
    #     for spec in self.specjalista:
    #         validate_choice(db, "Specjalista", spec)
    #     return self

class UserDisplay(UserBase):
    id_uzytkownika: int = Field(alias='ID_uzytkownika', serialization_alias='id_uzytkownika')
    
    class Config(): 
        from_attributes = True # to robi, że klasa UserDisplay rozumie, czyta obiekty sqlalchemy i jest w stanie zmapować na jsona
        # bez tego trzeba byłoby podawać dane w postaci dicta, jsona, a tak można 
        # If the schema is used to convert database objects to JSON responses, it needs from_attributes = True. If it only handles input data, it doesn't need this configuration.

class UserUpdate(BaseModel):
    """Schema for updating user information"""
    full_name: Optional[str] = Field(None, alias='Full_name', serialization_alias='full_name')
    role: Optional[RoleEnum] = Field(None, alias='Role', serialization_alias='role')
    status: Optional[StatusEnum] = Field(None, alias='Status', serialization_alias='status')
    specjalista: Optional[List[str]] = Field(None, alias='Specjalista', serialization_alias='specjalista')

    class Config:
        # validate_by_alias = True
        from_attributes = True

class UserSignIn(BaseModel):
    username: str
    password: str

class TokenRequest(BaseModel):
    refresh_token: str

from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field #, model_validator, field_validator
# import re

class CreateGrupa(BaseModel):
    nazwa_grupy: str = Field(..., alias="Nazwa_grupy")
    data_rozpoczecia: date = Field(..., alias="Data_rozpoczecia")
    data_zakonczenia: Optional[date] = Field(None, alias="Data_zakonczenia")
    typ_grupy: str = Field(..., alias="Typ_grupy")
    liczba_spotkan: Optional[int] = Field(None, alias="Liczba_spotkan")
    liczba_godzin: Optional[float] = Field(None, alias="Liczba_godzin")
    prowadzacy: Optional[List[int]] = Field(None)

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True

class DisplayProwadzacy(BaseModel):
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    full_name: str = Field(..., alias="Full_name")

class DisplayGrupa(CreateGrupa):
    id_grupy: int = Field(..., alias="ID_grupy")
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    created: datetime = Field(..., alias="Created")
    prowadzacy: Optional[List[DisplayProwadzacy]] = Field(None)


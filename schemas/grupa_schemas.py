from typing import Optional, List
from datetime import date, datetime
from pydantic import BaseModel, Field #, model_validator, field_validator
# import re

class GrupaCreate(BaseModel):
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

class ProwadzacyDisplay(BaseModel):
    # id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    full_name: str = Field(..., alias="Full_name")

class UczestnikGrupyDisplayShort(BaseModel):
    id_uczestnika_grupy: int = Field(..., alias="ID_uczestnika_grupy")

class GrupaDisplay(GrupaCreate):
    id_grupy: int = Field(..., alias="ID_grupy")
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    created: datetime = Field(..., alias="Created")
    last_modified: datetime = Field(..., alias="Last_modified")
    rezultaty: Optional[str] = Field(None, alias="Rezultaty")
    prowadzacy: Optional[List[ProwadzacyDisplay]] = Field(None)
    uczestnicy_grupy: Optional[List[UczestnikGrupyDisplayShort]] = Field(None)
    uczestnicy_count: int = Field(default=0)

class GrupaUpdate(GrupaCreate):
    nazwa_grupy: Optional[str] = Field(None, alias="Nazwa_grupy")
    data_rozpoczecia: Optional[date] = Field(None, alias="Data_rozpoczecia")
    typ_grupy: Optional[str] = Field(None, alias="Typ_grupy")


class UczestnikGrupyCreate(BaseModel):
    id_grupy: int = Field(..., alias="ID_grupy")
    id_pacjenta: int = Field(..., alias="ID_pacjenta")
    ukonczenie: Optional[bool] = Field(None, alias="Ukonczenie")
    rezultat: Optional[str] = Field(None, alias="Rezultat")

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True

class UczestnikDisplay(BaseModel):
    id_pacjenta: int = Field(..., alias="ID_pacjenta")
    imie: str = Field(..., alias="Imie")
    nazwisko: str = Field(..., alias="Nazwisko")

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True

class GrupaDisplayShort(BaseModel):
    id_grupy: int = Field(..., alias="ID_grupy")
    nazwa_grupy: str = Field(..., alias="Nazwa_grupy")

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True

class UczestnikGrupyDisplay(UczestnikGrupyCreate):
    id_uczestnika_grupy: int = Field(..., alias="ID_uczestnika_grupy")
    created: datetime = Field(..., alias="Created")
    last_modified: datetime = Field(..., alias="Last_modified")
    grupa: GrupaDisplayShort = Field(...)
    pacjent: UczestnikDisplay = Field(...)


class UczestnikGrupyUpdate(BaseModel):
    id_grupy: Optional[int] = Field(None, alias="ID_grupy")
    id_pacjenta: Optional[int] = Field(None, alias="ID_pacjenta")

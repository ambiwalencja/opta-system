from typing import Optional #, List, Any
from datetime import date #, datetime
from pydantic import BaseModel, Field #, model_validator, field_validator
# import re

class WizytaIndywidualnaCreate(BaseModel):
    id_pacjenta: int = Field(..., alias="ID_pacjenta")
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    data_wizyty: date = Field(..., alias="Data_wizyty")
    typ_wizyty: str = Field(..., alias="Typ_wizyty")
    liczba_godzin: float = Field(..., alias="Liczba_godzin")
    notatka_diagnoza_sytuacji: Optional[str] = Field(None, alias="Notatka_diagnoza_sytuacji")
    notatka_opis_sytuacji: Optional[str] = Field(None, alias="Notatka_opis_sytuacji")
    notatka_indywidualny_plan: Optional[str] = Field(None, alias="Notatka_indywidualny_plan")
    notatka_rezultaty: Optional[str] = Field(None, alias="Notatka_rezultaty")
    notatka_odeslanie_do_innych: Optional[str] = Field(None, alias="Notatka_odeslanie_do_innych")

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True

class WizytaIndywidualnaImport(WizytaIndywidualnaCreate):
    id_wizyty: int = Field(..., alias="ID_wizyty")
    id_uzytkownika: Optional[int] = Field(None, alias="ID_uzytkownika")

class WizytaIndywidualnaDisplay(BaseModel):
    id_wizyty: int = Field(..., alias="ID_wizyty")
    id_pacjenta: int = Field(..., alias="ID_pacjenta")
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    data_wizyty: date = Field(..., alias="Data_wizyty")
    typ_wizyty: str = Field(..., alias="Typ_wizyty")
    liczba_godzin: float = Field(..., alias="Liczba_godzin")
    

class WizytaIndywidualnaUpdate(WizytaIndywidualnaCreate):
    id_pacjenta: Optional[int] = Field(None, alias="ID_pacjenta")
    id_uzytkownika: Optional[int] = Field(None, alias="ID_uzytkownika")
    data_wizyty: Optional[date] = Field(None, alias="Data_wizyty")
    typ_wizyty: Optional[str] = Field(None, alias="Typ_wizyty")
    liczba_godzin: Optional[float] = Field(None, alias="Liczba_godzin")

class UserDisplayShort(BaseModel):
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")
    full_name: str = Field(..., alias="Full_name")

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True

class WizytaIndywidualnaDisplayDetails(BaseModel):
    id_wizyty: int = Field(..., alias="ID_wizyty")
    id_pacjenta: int = Field(..., alias="ID_pacjenta")
    data_wizyty: date = Field(..., alias="Data_wizyty")
    typ_wizyty: str = Field(..., alias="Typ_wizyty")
    liczba_godzin: float = Field(..., alias="Liczba_godzin")
    notatka_diagnoza_sytuacji: Optional[str] = Field(None, alias="Notatka_diagnoza_sytuacji")
    notatka_opis_sytuacji: Optional[str] = Field(None, alias="Notatka_opis_sytuacji")
    notatka_indywidualny_plan: Optional[str] = Field(None, alias="Notatka_indywidualny_plan")
    notatka_rezultaty: Optional[str] = Field(None, alias="Notatka_rezultaty")
    notatka_odeslanie_do_innych: Optional[str] = Field(None, alias="Notatka_odeslanie_do_innych")
    
    # User
    uzytkownik: UserDisplayShort = Field(...)
    


    
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import date, datetime

from schemas.grupa_schemas import UczestnikGrupyDisplay

class SpotkanieGrupoweCreate(BaseModel):
    id_grupy: int = Field(..., alias="ID_grupy")
    data_spotkania: date = Field(..., alias="Data_spotkania")
    liczba_godzin: Optional[float] = Field(None, alias="Liczba_godzin")
    obecni_uczestnicy: Optional[List[int]] = Field(None, alias="Obecni_uczestnicy")
    notatka_przebieg: Optional[str] = Field(None, alias="Notatka_przebieg")

    class Config():
        from_attributes = True
        validate_by_name = True
        validate_by_alias = True


class SpotkanieGrupoweDisplay(SpotkanieGrupoweCreate):
    id_spotkania: int = Field(..., alias='ID_spotkania') 
    obecni_uczestnicy: Optional[List[UczestnikGrupyDisplay]] = Field(None, alias="Obecni_uczestnicy")

class SpotkanieGrupoweDisplayShort(BaseModel):
    id_spotkania: int = Field(..., alias='ID_spotkania')
    id_grupy: int = Field(..., alias="ID_grupy")
    nazwa_grupy: str = Field(..., alias="Nazwa_grupy")
    data_spotkania: date = Field(..., alias="Data_spotkania")
    liczba_godzin: Optional[float] = Field(None, alias="Liczba_godzin")
    obecni_uczestnicy_count: Optional[int] = Field(None, alias="Obecni_uczestnicy_count")

class SpotkanieGrupoweUpdate(SpotkanieGrupoweCreate):
    id_grupy: Optional[int] = Field(None, alias="ID_grupy")
    data_spotkania: Optional[date] = Field(None, alias="Data_spotkania")

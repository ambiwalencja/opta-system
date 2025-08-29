from typing import Optional, List, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator

class CreatePacjent(BaseModel):
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika") # "..." means it's required
    data_zgloszenia: date = Field(..., alias="Data_zgloszenia")
    data_ostatniej_wizyty: Optional[date] = Field(None, alias="Data_ostatniej_wizyty")
    imie: str = Field(..., alias="Imie")
    nazwisko: str = Field(..., alias="Nazwisko")
    email: Optional[str] = Field(None, alias="Email")
    telefon: str = Field(..., alias="Telefon")
    dzielnica: str = Field(..., alias="Dzielnica")
    ulica: str = Field(..., alias="Ulica")
    nr_domu: int = Field(..., alias="Nr_domu")
    nr_mieszkania: Optional[int] = Field(None, alias="Nr_mieszkania")
    kod_pocztowy: Optional[str] = Field(None, alias="Kod_pocztowy")
    wiek: int = Field(..., alias="Wiek")
    status_zawodowy: str = Field(..., alias="Status_zawodowy")
    stan_cywilny: str = Field(..., alias="Stan_cywilny")
    wyksztalcenie: str = Field(..., alias="Wyksztalcenie")
    plec: str = Field(..., alias="Plec")
    zrodlo_informacji: str = Field(..., alias="Zrodlo_informacji")
    zrodlo_informacji_inne: Optional[str] = Field(None, alias="Zrodlo_informacji_inne")
    korzystanie_z_pomocy: List = Field(..., alias="Korzystanie_z_pomocy")
    korzystanie_z_pomocy_inne: Optional[str] = Field(None, alias="Korzystanie_z_pomocy_inne")
    placowka_kierujaca: str = Field(..., alias="Placowka_kierujaca")
    placowka_kierujaca_inna: Optional[str] = Field(None, alias="Placowka_kierujaca_inne")   
    niebieska_karta: bool = Field(..., alias="Niebieska_karta")
    niebieska_karta_inicjator: Optional[str] = Field(None, alias="Niebieska_karta_inicjator")
    grupa_robocza: Optional[bool] = Field(None, alias="Grupa_robocza")
    grupa_robocza_sklad: Optional[str] = Field(None, alias="Grupa_robocza_sklad")
    plan_pomocy: Optional[bool] = Field(None, alias="Plan_pomocy")
    plan_pomocy_opis: Optional[str] = Field(None, alias="Plan_pomocy_opis")
    narzedzia_prawne: Optional[bool] = Field(None, alias="Narzedzia_prawne")
    zawiadomienie: Optional[bool] = Field(None, alias="Zawiadomienie")
    postepowanie_cywilne: bool = Field(..., alias="Postepowanie_cywilne")
    postepowanie_karne: bool = Field(...,  alias="Postepowanie_karne")
    postepowanie_rodzinne: bool = Field(...,  alias="Postepowanie_rodzinne")
    liczba_dzieci: int = Field(..., alias="Liczba_dzieci")
    problemy: List = Field(...,  alias="Problemy")
    problemy_inne: Optional[str] = Field(None, alias="Problemy_inne")
    notatka_diagnoza_sytuacji: Optional[str] = Field(None, alias="Notatka_diagnoza_sytuacji")
    zaproponowane_wsparcie: List = Field(..., alias="Zaproponowane_wsparcie")
    zaproponowane_wsparcie_inne: Optional[str] = Field(None, alias="Zaproponowane_wsparcie_inne")
    ewaluacja: bool = Field(...,  alias="Ewaluacja")
    status_pacjenta: str = Field(...,  alias="Status_pacjenta")
    data_zakonczenia: Optional[date] = Field(None, alias="Data_zakonczenia")

    @model_validator(mode="after") # only validating, not overwriting
    def validate_conditional_fields(self):
        # If niebieska_karta is False or None, dependent fields must be empty
        if not self.niebieska_karta:
            if any([
                self.niebieska_karta_inicjator,
                self.grupa_robocza,
                self.grupa_robocza_sklad,
                self.plan_pomocy,
                self.plan_pomocy_opis,
                self.narzedzia_prawne,
                self.zawiadomienie
            ]):
                raise ValueError(
                    "When 'Niebieska_karta' is false or null, "
                    "fields from 'Niebieska_karta_inicjator' to 'Zawiadomienie' must be empty."
                )
        return self
    
    class Config():
        from_attributes = True # orm_mode = True - deprecated in v2, changed to from_attributes
        validate_by_name=True
        validate_by_alias=True
        # allow_population_by_field_name, populate_by_name - deprecated
    
    # # or modern way of setting up config
    # model_config = ConfigDict(
    #         validate_by_name=True,
    #         validate_by_alias=True
    #     )

class DisplayPacjent(BaseModel):
    imie: str = Field(..., alias="Imie")
    nazwisko: str = Field(..., alias="Nazwisko")
    data_zgloszenia: date = Field(..., alias="Data_zgloszenia")
    data_ostatniej_wizyty: Optional[date] = Field(None, alias="Data_ostatniej_wizyty")
    email: Optional[str] = Field(None, alias="Email")
    telefon: str = Field(..., alias="Telefon")
    dzielnica: str = Field(..., alias="Dzielnica")
    status_pacjenta: str = Field(...,  alias="Status_pacjenta")
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika")

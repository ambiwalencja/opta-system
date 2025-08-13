from typing import Optional, List, Any
from datetime import date, datetime
from pydantic import BaseModel, Field, model_validator

class ClientCreateOld(BaseModel):
    ID_uzytkownika: int
    Created: Optional[datetime] = None
    Last_modified: Optional[datetime] = None
    Data_zgloszenia: date
    Data_ostatniej_wizyty: Optional[date] = None
    Imie: str
    Nazwisko: str
    Email: Optional[str] = None
    Telefon: Optional[str] = None
    Dzielnica: Optional[str] = None
    Ulica: Optional[str] = None
    Nr_domu: Optional[int] = None
    Nr_mieszkania: Optional[int] = None
    Kod_pocztowy: Optional[str] = None
    Wiek: Optional[int] = None
    Status_zawodowy: Optional[str] = None
    Stan_cywilny: Optional[str] = None
    Wyksztalcenie: Optional[str] = None
    Plec: Optional[int] = None
    Zrodlo_informacji: Optional[str] = None
    Korzystanie_z_pomocy: Optional[Any] = None
    Placowka_kierujaca: Optional[str] = None
    Niebieska_karta: Optional[bool] = None
    Niebieska_karta_inicjator: Optional[str] = None
    Grupa_robocza: Optional[bool] = None
    Grupa_robocza_sklad: Optional[str] = None
    Plan_pomocy: Optional[bool] = None
    Plan_pomocy_opis: Optional[str] = None
    Narzedzia_prawne: Optional[bool] = None
    Zawiadomienie: Optional[bool] = None
    Postepowanie_cywilne: Optional[bool] = None
    Postepowanie_karne: Optional[bool] = None
    Postepowanie_rodzinne: Optional[bool] = None
    Liczba_dzieci: Optional[int] = None
    Problemy: Optional[Any] = None
    Notatka_diagnoza_sytuacji: Optional[str] = None
    Zaproponowane_wsparcie: Optional[Any] = None
    Ewaluacja: Optional[bool] = None
    Status_pacjenta: Optional[str] = None
    Data_zakonczenia: Optional[date] = None

    class Config:
        orm_mode = True

class ClientCreate(BaseModel):
    id_uzytkownika: int = Field(..., alias="ID_uzytkownika") # "..." means it's required
    data_zgloszenia: date = Field(..., alias="Data_zgloszenia")
    data_ostatniej_wizyty: Optional[date] = Field(None, alias="Data_ostatniej_wizyty")
    imie: str = Field(..., alias="Imie")
    nazwisko: str = Field(..., alias="Nazwisko")
    email: Optional[str] = Field(None, alias="Email")
    telefon: Optional[str] = Field(None, alias="Telefon")
    dzielnica: Optional[str] = Field(..., alias="Dzielnica")
    ulica: Optional[str] = Field(..., alias="Ulica")
    nr_domu: Optional[int] = Field(..., alias="Nr_domu")
    nr_mieszkania: Optional[int] = Field(None, alias="Nr_mieszkania")
    kod_pocztowy: Optional[str] = Field(None, alias="Kod_pocztowy")
    wiek: Optional[int] = Field(None, alias="Wiek")
    status_zawodowy: Optional[str] = Field(None, alias="Status_zawodowy")
    stan_cywilny: Optional[str] = Field(None, alias="Stan_cywilny")
    wyksztalcenie: Optional[str] = Field(None, alias="Wyksztalcenie")
    plec: Optional[int] = Field(None, alias="Plec")
    zrodlo_informacji: Optional[str] = Field(None, alias="Zrodlo_informacji")
    korzystanie_z_pomocy: Optional[Any] = Field(None, alias="Korzystanie_z_pomocy")
    placowka_kierujaca: Optional[str] = Field(None, alias="Placowka_kierujaca")
    niebieska_karta: Optional[bool] = Field(None, alias="Niebieska_karta")
    niebieska_karta_inicjator: Optional[str] = Field(None, alias="Niebieska_karta_inicjator")
    grupa_robocza: Optional[bool] = Field(None, alias="Grupa_robocza")
    grupa_robocza_sklad: Optional[str] = Field(None, alias="Grupa_robocza_sklad")
    plan_pomocy: Optional[bool] = Field(None, alias="Plan_pomocy")
    plan_pomocy_opis: Optional[str] = Field(None, alias="Plan_pomocy_opis")
    narzedzia_prawne: Optional[bool] = Field(None, alias="Narzedzia_prawne")
    zawiadomienie: Optional[bool] = Field(None, alias="Zawiadomienie")
    postepowanie_cywilne: Optional[bool] = Field(None, alias="Postepowanie_cywilne")
    postepowanie_karne: Optional[bool] = Field(None, alias="Postepowanie_karne")
    postepowanie_rodzinne: Optional[bool] = Field(None, alias="Postepowanie_rodzinne")
    liczba_dzieci: Optional[int] = Field(None, alias="Liczba_dzieci")
    problemy: Optional[Any] = Field(None, alias="Problemy")
    notatka_diagnoza_sytuacji: Optional[str] = Field(None, alias="Notatka_diagnoza_sytuacji")
    zaproponowane_wsparcie: Optional[Any] = Field(None, alias="Zaproponowane_wsparcie")
    ewaluacja: Optional[bool] = Field(None, alias="Ewaluacja")
    status_pacjenta: Optional[str] = Field(None, alias="Status_pacjenta")
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
    
    # # earlier version - silently nulling the fields
    # @model_validator(mode="before")
    # def clear_conditional_fields(cls, data):
    #     """
    #     If niebieska_karta is False (or 0), force related fields to None.
    #     Works whether data is a dict from JSON or already parsed values.
    #     """
    #     # In 'before' mode, `data` is a dict
    #     nk = data.get("Niebieska_karta") or data.get("niebieska_karta")
    #     if nk is False or nk == 0:
    #         data["Niebieska_karta_inicjator"] = None
    #         data["Grupa_robocza"] = None
    #         data["Grupa_robocza_sklad"] = None
    #         data["Plan_pomocy"] = None
    #         data["Plan_pomocy_opis"] = None
    #         data["Narzedzia_prawne"] = None
    #         data["Zawiadomienie"] = None
    #     return data
    
    class Config():
        orm_mode = True
        validate_by_name=True
        validate_by_alias=True
        # allow_population_by_field_name, populate_by_name - deprecated
    
    # # or modern way of setting up config
    # model_config = ConfigDict(
    #         validate_by_name=True,
    #         validate_by_alias=True
    #     )

class ClientDisplay(BaseModel):
    pass # TODO: zrobić
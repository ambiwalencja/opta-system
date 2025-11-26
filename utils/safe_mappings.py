from sqlalchemy import desc, Column
from db_models.client_data import Pacjent

SORTABLE_FIELDS = {
    "id_pacjenta": Pacjent.ID_pacjenta,
    "imie": Pacjent.Imie,
    "nazwisko": Pacjent.Nazwisko,
    "data_zgloszenia": Pacjent.Data_zgloszenia,
    "data_ostatniej_wizyty": Pacjent.Data_ostatniej_wizyty,
    "created": Pacjent.Created
}

FILTERING_FIELDS = {
    "dzielnica": Pacjent.Dzielnica,
    "data_zgloszenia": Pacjent.Data_zgloszenia, # TODO: tutaj trzeba rozdzielić na lata i miesiące
    "Niebieska_karta": Pacjent.Niebieska_karta,
    "Zaproponowane_wsparcie": Pacjent.Zaproponowane_wsparcie
}

SEARCHABLE_FIELDS = [Pacjent.Imie, Pacjent.Nazwisko, Pacjent.Email, Pacjent.Telefon]
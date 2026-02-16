from db_models.client_data import Pacjent

SORTABLE_FIELDS = {
    "ID_pacjenta": Pacjent.ID_pacjenta,
    "Imie": Pacjent.Imie,
    "Nazwisko": Pacjent.Nazwisko,
    "Data_zgloszenia": Pacjent.Data_zgloszenia,
    "Data_ostatniej_wizyty": Pacjent.Data_ostatniej_wizyty,
    "Created": Pacjent.Created
}

FILTERING_FIELDS = {
    "Dzielnica": Pacjent.Dzielnica,
    "Data_zgloszenia": Pacjent.Data_zgloszenia,
    "Niebieska_karta": Pacjent.Niebieska_karta,
    "Zaproponowane_wsparcie": Pacjent.Zaproponowane_wsparcie
}

SEARCHABLE_FIELDS = [Pacjent.Imie, Pacjent.Nazwisko, Pacjent.Email, Pacjent.Telefon]
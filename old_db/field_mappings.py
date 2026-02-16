# Mappings for converting old database field values to new database field values

# Single-choice field mappings - pacjenci
DZIELNICA_MAP = {
    1: "Bemowo",
    2: "Białołęka",
    3: "Bielany",
    4: "Mokotów",
    5: "Ochota",
    6: "Praga-Południe",
    7: "Praga-Północ",
    8: "Rembertów",
    9: "Śródmieście",
    10: "Targówek",
    11: "Ursus",
    12: "Ursynów",
    13: "Wawer",
    14: "Wesoła",
    15: "Wilanów",
    16: "Włochy",
    17: "Wola",
    18: "Żoliborz"
}

STATUS_ZAWODOWY_MAP = {
    1: "pracujący",
    2: "prowadzący działalność gospodarczą",
    3: "bezrobotny",
    4: "na urlopie macierzyńskim/wychowawczym",
    5: "na emeryturze/rencie",
    6: "pobierający zasiłek (np. z pomocy społecznej)",
    7: "uczący się"
}

STAN_CYWILNY_MAP = {
    1: "panna / kawaler",
    2: "mężatka / żonaty",
    3: "rozwiedziona/y / w separacji",
    4: "wdowa / wdowiec",
    5: "konkubinat"
}

WYKSZTALCENIE_MAP = {
    1: "podstawowe",
    2: "gimnazjalne",
    3: "ponadgimnazjalne",
    4: "zasadnicze zawodowe",
    5: "licencjat/inżynier",
    6: "wyższe pełne"
}

PLEC_MAP = {
    1: "Kobieta",
    2: "Mężczyzna"
}

ZRODLO_INFORMACJI_MAP = {
    1: "od znajomej/ego",
    2: "od rodziny",
    3: "z Internetu",
    4: "z instytucji",
    5: "z innej organizacji pozarządowej",
    6: "z ulotki",
    7: "ze spotkania informacyjnego",
    8: "z zespołu interdyscyplinarnego/grupy roboczej",
    9: "z innego źródła (podać jakie)"
}

PLACOWKA_KIERUJACA_MAP = {
    1: "zespół interdyscyplinarny/grupa robocza",
    2: "ośrodek pomocy społecznej",
    3: "poradnia PP",
    4: "sąd/kurator",
    5: "poradnia uzależnień",
    6: "inna placówka ochrony zdrowia",
    7: "inna organizacja pozarządowa",
    8: "ta sama organizacja pozarządowa",
    9: "z własnej inicjatywy",
    10: "inne - jakie?"
}

STATUS_PACJENTA_MAP = { # bo w stastusie nagle liczby nie były intami tylko stringami
    "1": "przekierowanie do innej placówki",
    "2": "aktywny, klient w kontakcie",
    "3": "zakończona pomoc",
    "4": "rezygnacja",
    "5": "kontakt zawieszony",
    "6": "klient powracający"
}

# Multiple-choice field mappings (as JSON arrays)
KORZYSTANIE_Z_POMOCY_MAP = {
    1: "nie korzysta",
    2: "ośrodek pomocy społecznej",
    3: "poradnia psych-pedagogiczna",
    4: "poradnia rodzinna",
    5: "poradnia odwykowa/DZRPA",
    6: "placówka ochrony zdrowia",
    7: "organizacja pozarządowa",
    8: "w ramach tej samej placówki",
    9: "inne - jakie?"
}

PROBLEMY_MAP = {
    1: "przemoc fizyczna",
    2: "przemoc psychiczna",        
    3: "przemoc seksualna",
    4: "przemoc ekonomiczna",
    5: "zaniedbanie",
    6: "problemy opiekuńczo-wychowawcze",
    7: "uzależnienia",
    8: "problemy materialno-bytowe",
    9: "niepełnosprawność/choroba",
    10: "sprawy okołorozwodowe",
    11: "inne - jakie?"
}

ZAPROPONOWANE_WSPARCIE_MAP = {
    1: "działania informacyjno-konsultacyjne",
    2: "konsultacje prawne",
    3: "konsultacje pedagogiczne",
    4: "konsultacje psychologiczne",
    5: "pomoc psychologiczna",
    6: "grupa wsparcia",
    7: "warsztat, trening",
    8: "inne - konsylium psycholog/prawnik",
    9: "inne - pomoc 'adwokata socjalnego'",
    10: "inne - konsultacje do grupy wsparcia",
    11: "inne - konsultacje do grupy rozwojowej",
    12: "inne - grupa o charakterze rozwojowym.", #TODO: uwaga tu jest kropka i w pozostałych miejscach też przy tej opcji. docelowo przy migracji usunąć.
    13: "inne - jakie?"
}

PACJENCI_COLUMN_MAPPING = {
        'numeridklienta': 'ID_pacjenta', # INFO: uwaga, pacjenci są identyfikowani po tym numerze (przy wizytach np), nie po zmiennej id_pacjenta!
        # pytanie, czy gdzieś jest uzywana zmienna id_pacjenta (która wygląda jak klucz główny w starej tabeli pacjenci)
        'rejestrator': 'ID_uzytkownika',  # to jest imię i nazwisko wpisywane z ręki w starej bazie
        'data_zgloszenia': 'Data_zgloszenia',
        'imie': 'Imie',
        'nazwisko': 'Nazwisko',
        'email': 'Email',
        'telefon': 'Telefon',
        'dzielnica': 'Dzielnica',
        'ulica': 'Ulica',
        'nrdomu': 'Nr_domu',
        'nrmieszkania': 'Nr_mieszkania',
        'kod': 'Kod_pocztowy',
        'wiek': 'Wiek',
        'statuspraca': 'Status_zawodowy',
        'stancyw': 'Stan_cywilny',
        'wyksztalcenie': 'Wyksztalcenie',
        'plec': 'Plec',
        'skadwie': 'Zrodlo_informacji',
        'skadwieinne': 'Zrodlo_informacji_inne',
        'czykorzysta': 'Korzystanie_z_pomocy',
        'czykorzystainne': 'Korzystanie_z_pomocy_inne',
        'ktokieruje': 'Placowka_kierujaca',
        'ktokierujeinne': 'Placowka_kierujaca_inne',
        'karta': 'Niebieska_karta',
        'kartainicjator': 'Niebieska_karta_inicjator',
        'gruparobocza': 'Grupa_robocza',    
        'skladgrupy': 'Grupa_robocza_sklad',
        'planpomocy': 'Plan_pomocy',
        'opisplanupomocy': 'Plan_pomocy_opis',
        'narzedziaprawne': 'Narzedzia_prawne',
        'zawiadomienie': 'Zawiadomienie',
        'postepowaniecyw': 'Postepowanie_cywilne',
        'postepowaniekar': 'Postepowanie_karne',
        'postepowanierod': 'Postepowanie_rodzinne',
        'czydzieci': 'Liczba_dzieci',
        'jakiproblem': 'Problemy',
        'jakiprobleminne': 'Problemy_inne',
        'rodzajwsparcia': 'Zaproponowane_wsparcie',
        'rodzajwsparciainne': 'Zaproponowane_wsparcie_inne',
        'zgoda': 'Ewaluacja',
        'status': 'Status_pacjenta',
        'data_zakonczenia': 'Data_zakonczenia',
    }

WIZYTY_COLUMN_MAPPING = {
        'id_wizyty': 'ID_wizyty',
        'id_pacjenta': 'ID_pacjenta',
       
        # brak 'ID_uzytkownika'!
        'data_wizyty': 'Data_wizyty',
        'specjalista': 'Typ_wizyty',
        'liczba_godzin': 'Liczba_godzin',
        'diagnoza_sytuacji': 'Notatka_diagnoza_sytuacji',
        'opis_sytuacji': 'Notatka_opis_sytuacji',
        'indywidualny_plan': 'Notatka_indywidualny_plan',
        'rezultaty': 'Notatka_rezultaty',
        'odeslanie_do_innych': 'Notatka_odeslanie_do_innych'

}

TYP_WIZYTY_INDYWIDUALNEJ_MAP = {
    1: 'specjalista ds. przeciwdziałania przemocy',
    2: 'adwokat socjalny',
    3: 'psycholog - konsultacja diagnostyczna',
    4: 'psycholog - konsultacja rodzicielska',
    5: 'prawnik - konsultacja / porada prawna',
    6: 'psycholog/terapeuta - wsparcie',
    7: 'konsultacje do grupy wsparcia i do grupy rozwojowej',
    17: 'indywidualne konsultacje w zespole psycholog-prawnik',
    19: 'indywidualne konsultacje do grupy trening antystresowy 2020'
}

NAZWA_GRUPY_MAP = {
    8: 'grupa wsparcia',
    9: 'grupa o charakterze rozwojowym',
    10: 'trening antystresowy',
    11: 'warsztat psychoedukacyjny 1',
    12: 'warsztat psychoedukacyjny 2',
    13: 'warsztat psychoedukacyjny 3',
    14: 'warsztat psychoedukacyjny 4',
    15: 'warsztat psychoedukacyjny 5',
    16: 'warsztat psychoedukacyjny 6',
    18: 'trening antystresowy 2020',
    20: 'trening antystresowy 2021 - grupa 1',
    21: 'trening antystresowy 2021 - grupa 2',
    22: 'grupa rozwojowa Jesień 2021',
    23: 'Grupa wsparcia 2021 - wiosna',
    24: 'Grupa wsparcia 2021 - jesień',
    25: 'Warsztat psychoedukacyjny 2021 - wiosna',
    26: 'Warsztat psychoedukacyjny 2021 - jesień',
    27: 'trening antystresowy 2022 - grupa 1',
    28: 'trening antystresowy 2022 - grupa 2',
    29: 'grupa rozwojowa Jesień 2022',
    30: 'Grupa wsparcia 2022 - wiosna',
    31: 'Grupa wsparcia 2022 - jesień',
    32: 'Warsztat psychoedukacyjny 2022 - wiosna',
    33: 'Warsztat psychoedukacyjny 2022 - jesień',
    34: 'grupa rozwojowa Wiosna 2023',
    35: 'trening antystresowy 2023',
    36: 'grupa dramaterapeutyczna 2023',
    37: 'trening antystresowy 2024',
    38: 'grupa dramaterapeutyczna 2024',
    39: 'grupa rozwojowa jesień 2023',
    40: 'grupa rozwojowa wiosna 2024',
    41: 'Grupa wsparcia 2023 - wiosna',
    42: 'Grupa wsparcia 2023 - jesień',
    43: 'Grupa wsparcia 2024 - wiosna',
    44: 'grupa rozwojowa jesień 2024',
    45: 'Grupa wsparcia 2024 - jesień',
    46: 'Grupa rozwojowa 2025 - wiosna',
    47: 'Grupa wsparcia 2025 - wiosna'
}

GRUPY_TABLE_MAP = {
    8: ['grupa wsparcia', '2020-01-01', 'grupa wsparcia'],
    9: ['grupa o charakterze rozwojowym', '2020-01-01', 'grupa o charakterze rozwojowym'],
    10: ['trening antystresowy', '2020-01-01', 'trening antystresowy'],
    11: ['warsztat psychoedukacyjny 1', '2020-01-01', 'warsztat psychoedukacyjny'],
    12: ['warsztat psychoedukacyjny 2', '2020-01-01', 'warsztat psychoedukacyjny'],
    13: ['warsztat psychoedukacyjny 3', '2020-01-01', 'warsztat psychoedukacyjny'],
    14: ['warsztat psychoedukacyjny 4', '2020-01-01', 'warsztat psychoedukacyjny'],
    15: ['warsztat psychoedukacyjny 5', '2020-01-01', 'warsztat psychoedukacyjny'],
    16: ['warsztat psychoedukacyjny 6', '2020-01-01', 'warsztat psychoedukacyjny'],
    18: ['trening antystresowy 2020', '2020-01-01', 'trening antystresowy'],
    20: ['trening antystresowy 2021 - grupa 1', '2021-01-01', 'trening antystresowy'],
    21: ['trening antystresowy 2021 - grupa 2', '2021-01-01', 'trening antystresowy'],
    22: ['grupa rozwojowa Jesień 2021', '2021-09-01', 'grupa o charakterze rozwojowym'],
    23: ['Grupa wsparcia 2021 - wiosna', '2021-03-01', 'grupa wsparcia'],
    24: ['Grupa wsparcia 2021 - jesień', '2021-09-01', 'grupa wsparcia'],
    25: ['Warsztat psychoedukacyjny 2021 - wiosna', '2021-03-01', 'warsztat psychoedukacyjny'],
    26: ['Warsztat psychoedukacyjny 2021 - jesień', '2021-09-01', 'warsztat psychoedukacyjny'],
    27: ['trening antystresowy 2022 - grupa 1', '2022-01-01', 'trening antystresowy'],
    28: ['trening antystresowy 2022 - grupa 2', '2022-01-01', 'trening antystresowy'],
    29: ['grupa rozwojowa Jesień 2022', '2022-09-01', 'grupa o charakterze rozwojowym'],
    30: ['Grupa wsparcia 2022 - wiosna', '2022-03-01', 'grupa wsparcia'],
    31: ['Grupa wsparcia 2022 - jesień', '2022-09-01', 'grupa wsparcia'],
    32: ['Warsztat psychoedukacyjny 2022 - wiosna', '2022-03-01', 'warsztat psychoedukacyjny'],
    33: ['Warsztat psychoedukacyjny 2022 - jesień', '2020-09-01', 'warsztat psychoedukacyjny'],
    34: ['grupa rozwojowa Wiosna 2023', '2023-03-01', 'grupa o charakterze rozwojowym'],
    35: ['trening antystresowy 2023', '2023-01-01', 'trening antystresowy'],
    36: ['grupa dramaterapeutyczna 2023', '2023-01-01', 'grupa wsparcia'], # TODO: zapytać jaki to ma być typ
    37: ['trening antystresowy 2024', '2024-01-01', 'trening antystresowy'],
    38: ['grupa dramaterapeutyczna 2024', '2024-01-01', 'grupa wsparcia'], # TODO: zapytać jaki to ma być typ
    39: ['grupa rozwojowa jesień 2023', '2023-09-01', 'grupa o charakterze rozwojowym'],
    40: ['grupa rozwojowa wiosna 2024', '2024-03-01', 'grupa o charakterze rozwojowym'],
    41: ['Grupa wsparcia 2023 - wiosna', '2023-03-01', 'grupa wsparcia'],
    42: ['Grupa wsparcia 2023 - jesień', '2023-09-01', 'grupa wsparcia'],
    43: ['Grupa wsparcia 2024 - wiosna', '2024-03-01', 'grupa wsparcia'],
    44: ['grupa rozwojowa jesień 2024', '2024-09-01', 'grupa o charakterze rozwojowym'],
    45: ['Grupa wsparcia 2024 - jesień', '2024-09-01', 'grupa wsparcia'],
    46: ['Grupa rozwojowa 2025 - wiosna', '2025-03-01', 'grupa o charakterze rozwojowym'],
    47: ['Grupa wsparcia 2025 - wiosna', '2025-03-01', 'grupa wsparcia']
}


SPOTKANIA_GRUPOWE_COLUMN_MAPPING = {
        'data_wizyty': 'Data_spotkania',
        'specjalista': 'Nazwa_grupy',
        'liczba_godzin': 'Liczba_godzin',
        'info_o_dzialaniach': 'Notatka_przebieg'
}

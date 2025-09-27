# Mappings for converting old database field values to new database field values

# Single-choice field mappings - pacjenci
DZIELNICA_MAP = {
    1: "Bemowo",
    2: "Białołęka",
    3: "Bielany",
    4: "Mokotów",
    5: "Ochota",
    6: "Praga Południe",
    7: "Praga Północ",
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

WSPARCIE_MAP = {
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
    12: "inne - grupa o charakterze rozwojowym.",
    13: "inne - jakie?"
}

COLUMN_MAPPING = {
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
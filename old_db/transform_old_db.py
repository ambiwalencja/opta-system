import pandas as pd
from old_db.data_import import import_table_to_dataframe
import re
from sqlalchemy.orm import Session


def transform_imported_table(table_name: str, db: Session):
    df = import_table_to_dataframe(table_name, db)
    if table_name == "pacjenci":
        df = transform_table_pacjenci(df)
    elif table_name == "wizyty":
        df = transform_table_wizyty(df)
    elif table_name == "groupvisits":
        df = transform_table_groupvisits(df)
    elif table_name == "users":
        df = transform_table_users(df)
    # elif table_name == "czykorzysta_unserialized":
    #     df = transform_table_czykorzysta(df)
    # elif table_name == "jakiproblem_unserialized":
    #     df = transform_table_jakiproblem(df)
    # elif table_name == "propozycja_unserialized":
    #     df = transform_table_rodzajwsparcia(df)
    else:
        raise ValueError(f"Unknown table name: {table_name}")
    filename = f"test_table_import_after_transform_{table_name}.csv"
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        df.to_csv(f, index=False)
        print(f"Transformed data saved to {f}")
    print("Transformed DataFrame:")
    print(df.head())
    return df

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

STATUS_PACJENTA_MAP = {
    1: "przekierowanie do innej placówki",
    2: "aktywny, klient w kontakcie",
    3: "zakończona pomoc",
    4: "rezygnacja",
    5: "kontakt zawieszony",
    6: "klient powracający"
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



def parse_php_array(php_string: str) -> list:
    """Extract numbers from PHP serialized array string."""
    # Find all numbers after s:1:" pattern
    numbers = re.findall(r's:1:"(\d+)"', php_string)
    return [int(num) for num in numbers]

def transform_multiple_choice(df: pd.DataFrame, col: str, mapping: dict):
    """Transform PHP serialized arrays into lists of mapped values."""
    if col in df.columns:
        df[col] = df[col].apply(
            lambda x: [mapping[num] for num in parse_php_array(str(x))] if pd.notna(x) else []
        )
    return df


def transform_table_pacjenci(df: pd.DataFrame):
    # Rename columns to match new schema
    print("1")
    column_mapping = {
        'id_pacjenta': 'ID_pacjenta',
        'rejestrator': 'ID_uzytkownika',  # This will need to be mapped to the new user IDs
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
        'czykorzysta': 'Korzystanie_z_pomocy',
        'ktokieruje': 'Placowka_kierujaca',
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
        'rodzajwsparcia': 'Zaproponowane_wsparcie',
        'zgoda': 'Ewaluacja',
        'status': 'Status_pacjenta',
        'data_zakonczenia': 'Data_zakonczenia',

        # nridklienta - gdzie to identyfikuje pacjenta? w wizytach id_pacjenta pasuje jako identyfikator
        # skadwieinne, czykorzystainne, ktokierujeinne, jakiprobleminne, rodzajwsparciainne - tutaj będę musiała pomyśleć
        # sadowe, postępowanie - na razie nie przenosimy, stare zmienne
    }
    print("2")
    df = df.rename(columns=column_mapping)

    # Recode single-choice fields
    print("3")
    df['Dzielnica'] = df['Dzielnica'].map(DZIELNICA_MAP)
    df['Status_zawodowy'] = df['Status_zawodowy'].map(STATUS_ZAWODOWY_MAP)
    df['Stan_cywilny'] = df['Stan_cywilny'].map(STAN_CYWILNY_MAP)
    df['Wyksztalcenie'] = df['Wyksztalcenie'].map(WYKSZTALCENIE_MAP)
    df['Plec'] = df['Plec'].map(PLEC_MAP)
    df['Zrodlo_informacji'] = df['Zrodlo_informacji'].map(ZRODLO_INFORMACJI_MAP)
    df['Placowka_kierujaca'] = df['Placowka_kierujaca'].map(PLACOWKA_KIERUJACA_MAP)
    df['Status_pacjenta'] = df['Status_pacjenta'].map(STATUS_PACJENTA_MAP)
    print("4")
    # # Convert multiple-choice fields to JSON arrays
    # if 'czykorzysta' in df.columns:
    #     df['Korzystanie_z_pomocy'] = df['czykorzysta'].apply(lambda x: [KORZYSTANIE_Z_POMOCY_MAP[int(i)] for i in str(x).split(',') if i.isdigit()])
        
    # if 'jakiproblem' in df.columns:
    #     df['Problemy'] = df['jakiproblem'].apply(lambda x: [PROBLEMY_MAP[int(i)] for i in str(x).split(',') if i.isdigit()])
    
    # if 'rodzajwsparcia' in df.columns:
    #     df['Zaproponowane_wsparcie'] = df['rodzajwsparcia'].apply(lambda x: [WSPARCIE_MAP[int(i)] for i in str(x).split(',') if i.isdigit()])

    # Convert multiple-choice fields
    df = transform_multiple_choice(df, 'Korzystanie_z_pomocy', KORZYSTANIE_Z_POMOCY_MAP)
    df = transform_multiple_choice(df, 'Problemy', PROBLEMY_MAP)
    df = transform_multiple_choice(df, 'Zaproponowane_wsparcie', WSPARCIE_MAP)
    print("5")

    # Convert boolean fields
    boolean_columns = ['Niebieska_karta', 'Grupa_robocza', 'Plan_pomocy', 'Narzedzia_prawne', 'Zawiadomienie', 'Ewaluacja',
                       'Postepowanie_cywilne', 'Postepowanie_karne', 'Postepowanie_rodzinne']
    for col in boolean_columns:
        if col in df.columns:
            df[col] = df[col].map({1: True, 2: False, 0: None})
# TODO: tutaj się zatrzymałam tutaj sprawdzić i kontynuować
    return df

def transform_table_wizyty(df: pd.DataFrame):
    pass

def transform_table_groupvisits(df: pd.DataFrame):
    pass

def transform_table_users(df: pd.DataFrame):
    pass

# TODO: zastanowić się, czy może te tabele analogiczne się nie przydadzą, bo można one-hoty lepiej raportować
def transform_table_czykorzysta(df: pd.DataFrame):
    pass

def transform_table_jakiproblem(df: pd.DataFrame):
    pass

def transform_table_rodzajwsparcia(df: pd.DataFrame):
    pass
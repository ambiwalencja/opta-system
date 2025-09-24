import pandas as pd
from old_db.data_import import import_table_to_dataframe
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from old_db.field_mappings import DZIELNICA_MAP, STATUS_ZAWODOWY_MAP, STAN_CYWILNY_MAP, WYKSZTALCENIE_MAP, PLEC_MAP, ZRODLO_INFORMACJI_MAP, PLACOWKA_KIERUJACA_MAP, STATUS_PACJENTA_MAP, KORZYSTANIE_Z_POMOCY_MAP, PROBLEMY_MAP, WSPARCIE_MAP, COLUMN_MAPPING

def transform_imported_table(table_name: str, db_old: Session, db_new: Session) -> pd.DataFrame:
    df = import_table_to_dataframe(table_name, db_old)
    if table_name == "pacjenci":
        df = transform_table_pacjenci(df, db_new)
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
    try:
        with open(filename, 'w', newline='', encoding='utf-8') as f:
            df.to_csv(f, index=False)
            print(f"Transformed data saved to {f}")
    except Exception as e:
        print(f"Error saving transformed data to {filename}: {e}")
    print("Transformed DataFrame:")
    print(df.head(20))
    return df

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

def transform_column_id_uzytkownika(user_column_in_pacjenci: pd.Series):
    recoding_user_dict = {
        'Aldona Żejmo-Kudelska Joanna Rossa': 'Aldona Żejmo-Kudelska',
        'Marta Witek - Zegan ': 'Marta Witek',
        'Marta Witek-Zegan': 'Marta Witek',
        'Katarzyna Przyborowska i Marlena Dałek': 'Katarzyna Przyborowska',
        'Monika krzemieniewska': 'Monika Krzemieniewska',
        'Agnieszka Pawłowska-Frycowska': 'Agnieszka Pawłowska-Fryckowska',
        'I.Rokita': 'Izabela Rokita',
        'Iza Rokita': 'Izabela Rokita',
        'I. Rokita': 'Izabela Rokita',
        'Beata szymańska': 'Beata Szymańska',
        'Krzemieniecka Monika': 'Monika Krzemieniewska',
        'Monika Krzemieniecka': 'Monika Krzemieniewska'
    } # pozostałe wartości w tej metodzie zostaną niezmienione
    return user_column_in_pacjenci.replace(recoding_user_dict)


def replace_user_names_with_ids(user_column_in_pacjenci: pd.Series, df_users: pd.DataFrame):
    if df_users is None or df_users.empty:
        raise HTTPException(
            status_code=400,
            detail="No user data"
        )
    lookup_series = df_users.set_index('Full_name')['ID_uzytkownika']
    return user_column_in_pacjenci.map(lookup_series).fillna(-1) # if doesn't match, will be NaN so added .fillna(-1)) for nocrash xD

def clean_phone_numbers(phone_column: pd.Series) -> pd.Series:
    """Clean phone numbers by removing non-digit characters and set incorrect numbers as Null."""
    cleaned_phone_column = phone_column.astype(str).str.replace(r'\D', '', regex=True)
    invalid_mask = (~cleaned_phone_column.str.match(r'^\d{9}$')) | (cleaned_phone_column == '000000000')
    cleaned_phone_column.loc[invalid_mask] = None
    return cleaned_phone_column

def transform_table_pacjenci(df: pd.DataFrame, db: Session):
    # Rename columns to match new schema
    df = df.rename(columns=COLUMN_MAPPING)
    
    # Delete unnecessary columns
    columns_to_drop = ['id_pacjenta', 'data1konsultacji', 'sadowe', 'postępowanie'] # te dwie ostatnie to stare zmienne
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])

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
    
    # recode specific columns
    df['ID_uzytkownika'] = transform_column_id_uzytkownika(df['ID_uzytkownika'])
    df['ID_uzytkownika'] = replace_user_names_with_ids(df['ID_uzytkownika'], import_table_to_dataframe('users', db, 'user_data'))
    df['Telefon'] = clean_phone_numbers(df['Telefon'])
    return df

def transform_table_wizyty(df: pd.DataFrame):
    # TODO: zacząć od podzielenia na wizyty indywidualne (wartość 1) i grupowe (wartość 2) chociaż nie do końca
    column_mapping = {
        'id_pacjenta': 'ID_pacjenta',
        'id_wizyty': 'ID_wizyty',
        # brak 'ID_uzytkownika'!
        'data_wizyty': 'Data',
        'specjalista': 'Specjalista',
        'liczba_godzin': 'Liczba_godzin',
        'diagnoza_sytuacji': 'Notatka_diagnoza_sytuacji',
        'opis_sytuacji': 'Notatka_opis_sytuacji',
        'indywidualny_plan': 'Notatka_indywidualny_plan',
        'rezultaty': 'Notatka_rezultaty',
        'odeslanie_do_innych': 'Notatka_odeslanie_do_innych'
    }
    df = df.rename(columns=column_mapping)
    return df

def transform_table_groupvisits(df: pd.DataFrame):
    return df

def transform_table_users(df: pd.DataFrame):
    return df

def transform_table_czykorzysta(df: pd.DataFrame):
    return df

def transform_table_jakiproblem(df: pd.DataFrame):
    return df

def transform_table_rodzajwsparcia(df: pd.DataFrame):
    return df
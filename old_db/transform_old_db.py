import pandas as pd
from old_db.data_import import import_table_to_dataframe
import re
from sqlalchemy.orm import Session
from fastapi import HTTPException
from old_db import field_mappings

def transform_imported_table(old_db_table_name: str, new_db_table_name: str, db_old: Session, db_new: Session) -> pd.DataFrame:
    df = import_table_to_dataframe(old_db_table_name, db_old)
    if old_db_table_name == "pacjenci":
        df = transform_table_pacjenci(df, db_new)
    elif old_db_table_name == "wizyty":
        if new_db_table_name == "wizyty_indywidualne":
            df = transform_table_wizyty_indywidualne(df)
        elif new_db_table_name == "spotkania_grupowe":
            df = transform_table_spotkania_grupowe(df)
        elif new_db_table_name == "uczestnicy_grupy":
            df = transform_table_uczestnicy_grupy(df)
        else: 
            raise ValueError(f"Unknown new_db_table_name for wizyty: {new_db_table_name}")
    elif old_db_table_name == "groupvisits":
        df = transform_table_groupvisits(df)
    else:
        raise ValueError(f"Unknown table name: {old_db_table_name}")
    filename = f"test_table_import_after_transform_{old_db_table_name}.csv"
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
    df_users_unique = df_users.drop_duplicates(subset=['Full_name'], keep='last')
    lookup_series = df_users_unique.set_index('Full_name')['ID_uzytkownika']
    # print(lookup_series.head(5))
    try:
        user_column_in_pacjenci_after_mapping = user_column_in_pacjenci.map(lookup_series).fillna(1) # if doesn't match, will be NaN so added .fillna(1)) for nocrash xD
    except Exception as e:
        print(f"Error during mapping: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error during user ID mapping: {e}"
        )
    return user_column_in_pacjenci_after_mapping

def clean_phone_numbers(phone_column: pd.Series) -> pd.Series:
    """Clean phone numbers by removing non-digit characters and set incorrect numbers as Null."""
    cleaned_phone_column = phone_column.astype(str).str.replace(r'\D', '', regex=True)
    invalid_mask = (~cleaned_phone_column.str.match(r'^\d{9}$')) | (cleaned_phone_column == '000000000')
    cleaned_phone_column.loc[invalid_mask] = None
    return cleaned_phone_column

def transform_table_pacjenci(df: pd.DataFrame, db: Session):
    # Delete unnecessary columns
    columns_to_drop = ['id_pacjenta', 'data1konsultacji', 'sadowe', 'postępowanie'] # te dwie ostatnie to stare zmienne
    # TODO: zapytac mamę, czy chce, eby zrobić jeszcze jedną kolumnę "postępowanie" boolean, która będzie True, jeśli którakolwiek z postępowanie_cywilne, postępowanie_karne, postępowanie_rodzinne jest True, i wtedy do niej dokleimy wartość ze starszych danych, kiedy była tylko jedna kolumna postępowanie
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    # Rename columns to match new schema
    df = df.rename(columns=field_mappings.PACJENCI_COLUMN_MAPPING)
    # organizing columns - move ID_pacjenta to front and sort rows by it
    cols = df.columns.tolist()
    cols.insert(0, cols.pop(cols.index('ID_pacjenta')))
    df = df[cols]
    df = df.sort_values(by='ID_pacjenta', ascending=True)

    # Recode single-choice fields
    df['Dzielnica'] = df['Dzielnica'].map(field_mappings.DZIELNICA_MAP)
    df['Status_zawodowy'] = df['Status_zawodowy'].map(field_mappings.STATUS_ZAWODOWY_MAP)
    df['Stan_cywilny'] = df['Stan_cywilny'].map(field_mappings.STAN_CYWILNY_MAP)
    df['Wyksztalcenie'] = df['Wyksztalcenie'].map(field_mappings.WYKSZTALCENIE_MAP)
    df['Plec'] = df['Plec'].map(field_mappings.PLEC_MAP)
    df['Zrodlo_informacji'] = df['Zrodlo_informacji'].map(field_mappings.ZRODLO_INFORMACJI_MAP)
    df['Placowka_kierujaca'] = df['Placowka_kierujaca'].map(field_mappings.PLACOWKA_KIERUJACA_MAP)
    df['Status_pacjenta'] = df['Status_pacjenta'].map(field_mappings.STATUS_PACJENTA_MAP)

    # Convert multiple-choice fields
    df = transform_multiple_choice(df, 'Korzystanie_z_pomocy', field_mappings.KORZYSTANIE_Z_POMOCY_MAP)
    df = transform_multiple_choice(df, 'Problemy', field_mappings.PROBLEMY_MAP)
    df = transform_multiple_choice(df, 'Zaproponowane_wsparcie', field_mappings.WSPARCIE_MAP)

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

def transform_table_wizyty_indywidualne(df: pd.DataFrame):
    individual_visits_list = [1, 2, 3, 4, 5, 6, 7, 17, 19]
    df = df.loc[df['specjalista'].isin(individual_visits_list)] # wybieramy tylko indywidualne
    
    columns_to_drop = ['miesiac', 'rok', 'ind_grupowa', 'zaliczone', 'info_o_dzialaniach']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    df = df.rename(columns=field_mappings.WIZYTY_COLUMN_MAPPING)
    df = df.sort_values(by='ID_wizyty', ascending=True)
    df['Typ_wizyty'] = df['Typ_wizyty'].map(field_mappings.TYP_WIZYTY_MAP)
    recoding_user_dict = {
    'prawnik - konsultacja /porada prawna': 'prawnik - konsultacja / porada prawna'
    }
    df['Typ_wizyty'] = df['Typ_wizyty'].replace(recoding_user_dict)
    df['ID_uzytkownika'] = 1
    return df

def transform_table_spotkania_grupowe(df: pd.DataFrame):
    group_visits_list = range(8, 34)
    group_visits_list.remove(17, 19)
    df = df.loc[df['specjalista'].isin(group_visits_list)] 

    columns_to_drop = ['miesiac', 'rok', 'ind_grupowa', 'diagnoza_sytuacji', 'opis_sytuacji', 'indywidualny_plan', 'rezultaty', 'odeslanie_do_innych']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    # to jeszcze niegotowe
    return df

def transform_table_uczestnicy_grupy(df: pd.DataFrame):
    return df

def transform_table_groupvisits(df: pd.DataFrame):
    return df

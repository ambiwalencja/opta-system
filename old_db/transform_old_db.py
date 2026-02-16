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
            df = transform_table_wizyty_indywidualne(df, db_old, db_new)
        elif new_db_table_name == "spotkania_grupowe":
            df = transform_table_spotkania_grupowe(df, db_new)
        elif new_db_table_name == "uczestnicy_grupy":
            df = transform_table_uczestnicy_grupy(df, db_new)
        else: 
            raise ValueError(f"Unknown new_db_table_name for wizyty: {new_db_table_name}")
    elif old_db_table_name == "groupvisits":
        df = transform_table_groupvisits(df)
    else:
        raise ValueError(f"Unknown table name: {old_db_table_name}")
    filename = f"test_table_import_after_transform_{new_db_table_name}.csv"
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
    print("Replacing user names with IDs...")
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

def correct_multiple_choice_other_values(df: pd.DataFrame, col: str, col_detail: str):
    """Correct 'Other' values in multiple-choice fields, where detail for other is provided."""    
    # # The Pandas Way
    # df[col] = df.apply(
    #     lambda row: row[col] + ["inne - jakie?"] 
    #     if (row[col_detail] != "" and row[col_detail] != None and "inne - jakie?" not in row[col]) 
    #     else row[col], 
    #     axis=1
    # )

    # The Native Python Way
    df[col] = [
        original_list + ["inne - jakie?"] if (other != "" and other != None and "inne - jakie?" not in original_list) else original_list
        for other, original_list in zip(df[col_detail], df[col])
    ]
    return df

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

    # df = transform_multiple_choice(df, 'Korzystanie_z_pomocy', field_mappings.KORZYSTANIE_Z_POMOCY_MAP)
    # df = transform_multiple_choice(df, 'Problemy', field_mappings.PROBLEMY_MAP)
    # df = transform_multiple_choice(df, 'Zaproponowane_wsparcie', field_mappings.ZAPROPONOWANE_WSPARCIE_MAP)

    multiple_choice_fields = ['Korzystanie_z_pomocy', 'Problemy', 'Zaproponowane_wsparcie']
    for field in multiple_choice_fields:
        mapping = getattr(field_mappings, f"{field}_MAP".upper(), {})
        df = transform_multiple_choice(df, field, mapping)
        df = correct_multiple_choice_other_values(df, field, f"{field}_inne")

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

def transform_table_wizyty_indywidualne(df: pd.DataFrame, old_db: Session, new_db: Session):
    df = df.loc[df['specjalista'].isin(field_mappings.TYP_WIZYTY_INDYWIDUALNEJ_MAP.keys())]
    # df = df.loc[df['specjalista'] == 19]
    # df = df.head(50) # tylko do testów

    columns_to_drop = ['miesiac', 'rok', 'ind_grupowa', 'zaliczone', 'info_o_dzialaniach']
    df = df.drop(columns=[col for col in columns_to_drop if col in df.columns])
    
    df = df.rename(columns=field_mappings.WIZYTY_COLUMN_MAPPING)
    df = df.sort_values(by='ID_wizyty', ascending=True)
    df['Typ_wizyty'] = df['Typ_wizyty'].map(field_mappings.TYP_WIZYTY_INDYWIDUALNEJ_MAP)
    
    # Adding ID_uzytkownika from rejestr table through username and id_wizyty
    df_usernames = import_table_to_dataframe('rejestr', old_db)
    df_usernames = df_usernames.loc[df_usernames['modul'] == 'addvisit']
    df_usernames = df_usernames[['relid', 'operator']].rename(columns={'relid': 'ID_wizyty', 'operator': 'Username'})
    df = df.merge(df_usernames, on='ID_wizyty', how='left')

    df_users = import_table_to_dataframe('users', new_db, 'user_data')
    df_users = df_users[['ID_uzytkownika', 'Username']]
    df = df.merge(df_users, on='Username', how='left')
    df = df.drop(columns=['Username'])
    df['ID_uzytkownika'] = df['ID_uzytkownika'].fillna(1)
    return df

def transform_table_spotkania_grupowe(df: pd.DataFrame, new_db: Session):
    df = df.loc[df['specjalista'].isin(field_mappings.NAZWA_GRUPY_MAP.keys())]
    df.loc[:, 'specjalista'] = df['specjalista'].map(field_mappings.NAZWA_GRUPY_MAP).astype(str)
    df = df[['id_pacjenta', 'data_wizyty', 'specjalista', 'liczba_godzin', 'info_o_dzialaniach']]
    df = df.rename(columns=field_mappings.SPOTKANIA_GRUPOWE_COLUMN_MAPPING)
    df = df.rename(columns={'id_pacjenta': 'ID_pacjenta'})

    df_grupy = import_table_to_dataframe('grupy', new_db, 'client_data')
    df_grupy = df_grupy[['ID_grupy', 'Nazwa_grupy']]
    df_uczestnicy = import_table_to_dataframe('uczestnicy_grupy', new_db, 'client_data')
    df_uczestnicy = df_uczestnicy[['ID_uczestnika_grupy', 'ID_pacjenta', 'ID_grupy']]
    # print(f'df_uczestnicy head:\n{df_uczestnicy.head(10)}')
    df = df.merge(df_grupy, on='Nazwa_grupy', how='left')
    df = df.merge(df_uczestnicy, on=['ID_pacjenta', 'ID_grupy'], how='left')

    aggregation_rules = {
        'ID_uczestnika_grupy': lambda x: [int(v) for v in x.dropna()],          # Make a list of IDs
        'Liczba_godzin': 'first',             # Just take the first location found
        'Notatka_przebieg': lambda x: ' | '.join(x.dropna().astype(str).unique()) # Join unique values into a single string
    }
   # print(f'kolumny przed groupby: {df.columns.tolist()}')
    df = df.groupby(['Data_spotkania', 'ID_grupy']).agg(aggregation_rules).reset_index()
    df = df.rename(columns={'ID_uczestnika_grupy': 'Obecni_uczestnicy'})
    df = df.sort_values(by='Data_spotkania', ascending=True)

    return df

def transform_table_uczestnicy_grupy(df: pd.DataFrame, db: Session):
    df = df.loc[df['specjalista'].isin(field_mappings.NAZWA_GRUPY_MAP.keys())] 
    # df = df[['id_wizyty', 'id_pacjenta', 'data_wizyty', 'specjalista', 'diagnoza_sytuacji', 'opis_sytuacji', 'indywidualny_plan', 'rezultaty', 'zaliczone']]
    df = df[['id_pacjenta', 'specjalista', 'rezultaty', 'zaliczone']]

    # Fix group identification through group name
    from old_db.field_mappings import NAZWA_GRUPY_MAP
    df['Nazwa_grupy'] = df['specjalista'].map(NAZWA_GRUPY_MAP)
    from db_models.client_data import Grupa
    grupy = db.query(Grupa).all()
    grupa_name_to_id = {grupa.Nazwa_grupy: grupa.ID_grupy for grupa in grupy}
    df['ID_grupy'] = df['Nazwa_grupy'].map(grupa_name_to_id)

    df = df.rename(columns={'rezultaty': 'Rezultat', 'zaliczone': 'Ukonczenie', 'id_pacjenta': 'ID_pacjenta', 'id_grupy': 'ID_grupy'})
    df = df.drop(columns=['specjalista', 'Nazwa_grupy'])

    # recode ukonczenie
    df['Ukonczenie'] = df['Ukonczenie'].map({1: True, 2: False, 0: None})
     # fix date
    # df['data_wizyty'] = pd.to_datetime(df['data_wizyty']).dt.date

    # all notes into one column 'rezultat'
    # df['rezultat'] = df[['data_wizyty', 'diagnoza_sytuacji', 'opis_sytuacji', 'indywidualny_plan']].fillna('').apply(lambda row: '; '.join(row.astype(str)), axis=1)

    # print(f'rezultat po połączeniu: {df["rezultat"].head(20)}')
    # df['rezultat'] = df.groupby(['id_pacjenta', 'specjalista'])['rezultat'].transform(lambda x: ' | '.join(x))
    # print(f'rezultat po groupby: {df["rezultat"].head(20)}')
    # df = df.drop(columns=['data_wizyty', 'diagnoza_sytuacji', 'opis_sytuacji', 'indywidualny_plan'])
    
    # print(f'przed usunięciem duplikatów: {df.head(20)}')
    df = df.drop_duplicates(subset=['ID_pacjenta', 'ID_grupy'], keep='last')
    # print(f'po usunięciu duplikatów: {df.head(20)}')
    return df

def transform_table_groupvisits(df: pd.DataFrame):
    return df

def merge_duplicate_rows(df: pd.DataFrame, subset_cols: list, agg_dict: dict) -> pd.DataFrame:
    df_merged = df.groupby(subset_cols).agg(agg_dict).reset_index()
    # once: we have to identify
    # second: marge data from two or more rows
    # third: update pacjent id's in other tables
    return df_merged
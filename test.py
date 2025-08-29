import pandas as pd

filename = "test_table_import_after_transform_wizyty.csv"
# TODO: tutaj sprawdzić jacy są specjaliści

with open(filename, 'r', encoding='utf-8') as f:
    df = pd.read_csv(f)
    print(type(df["ID_uzytkownika"]))

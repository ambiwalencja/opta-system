import pandas as pd

filename = "test_table_import_after_transform_wizyty.csv"
filename2 = "test_table_import_after_transform_pacjenci.csv"

with open(filename, 'r', encoding='utf-8') as f:
    df = pd.read_csv(f)
    print(df["Specjalista"].unique())

import pandas as pd
from datetime import datetime
from fastapi import HTTPException
from sqlalchemy.orm import Session
from db.db_connect import SessionLocal  # or your session maker
from db_models.client_data import Grupa
import pandas as pd

filename = "test_table_import_after_transform_wizyty.csv"
filename2 = "test_table_import_after_transform_pacjenci.csv"
db: Session = SessionLocal()

with open(filename, 'r', encoding='utf-8') as f:
    df = pd.read_csv(f).head(10)
    # for index, row in df.iterrows():
    #     print(type(row))
    #     pacjent_data = row.to_dict()
    #     print(type(pacjent_data))
    #     print(pacjent_data)
    print(df.head(5))
    # df = df[['id_wizyty', 'id_pacjenta', 'data_wizyty', 'specjalista', 'diagnoza_sytuacji', 'opis_sytuacji', 'indywidualny_plan', 'rezultaty', 'zaliczone']]
    # df = df.drop_duplicates(subset=['id_pacjenta', 'specjalista'], keep='first') nie można tego zrobić, bo mogą być notatki po kilku wizytach.
    # więc potrzebujemy iterowac po wizytach i dopisywać do pola "Rezultaty" notatki z kolejnych wizyt
    grupy = db.query(Grupa).all()
    grupa_name_to_id = {grupa.Nazwa_grupy: grupa.ID_grupy for grupa in grupy}
    print (grupa_name_to_id)
    # df['id_grupy'] = df['specjalista'].map(grupa_name_to_id)
    # df['rezultat'] = df.groupby(['id_pacjenta', 'specjalista'])['data_wizyty', 'diagnoza_sytuacji', 'opis_sytuacji', 'indywidualny_plan'].agg(lambda x: ' '.join(x.dropna().astype(str))).reset_index(level=[0,1], drop=True)



    # df = df.head(10)
    # print(type(df['Data_zgloszenia'].iloc[0]))
    # for index, row in df.iterrows():
    #     try:
    #         # Convert row to dict and create CreatePacjent object
    #         pacjent_data = row.to_dict()
            
    #         # Convert date strings to date objects
    #         for date_field in ['Data_zgloszenia', 'Data_zakonczenia', 'Data_ostatniej_wizyty']:
    #             if date_field in pacjent_data and pacjent_data[date_field]:
    #                 try:
    #                     pacjent_data[date_field] = str(pacjent_data[date_field]).split(' ')[0]  # In case there's a time part
    #                     pacjent_data[date_field] = datetime.strptime(
    #                         pacjent_data[date_field], '%Y-%m-%d'
    #                     ).date()
    #                 except ValueError as e:
    #                     raise HTTPException(
    #                         status_code=400,
    #                         detail=f"Invalid date format in row {index} for field {date_field}: {str(e)}"
    #                     )
    #     except HTTPException as he:
    #         error_count += 1
    #         errors.append(str(he.detail))
    #         print(f"HTTP Error at row {index}: {he.detail}")
    #         continue


# model tabeli Users
from sqlalchemy import Column, Integer, String, DateTime, Boolean, Date, JSON
from db.db_connect import Base

class Pacjent(Base):
    __tablename__ = "pacjenci"
    ID_pacjenta = Column(Integer, primary_key=True)
    ID_uzytkownika = Column(Integer) # osoba rejestrująca
    Timestamp = Column(DateTime)
    Data_zgloszenia = Column(Date)
    # data1konsultacji - niepotrzebna bo to mamy w tabeli wizyt
    Imie = Column(String)
    Nazwisko = Column(String)
    Email = Column(String)
    Telefon = Column(String)
    Dzielnica = Column(String)
    Ulica = Column(String)
    Nr_domu = Column(Integer)
    Nr_mieszkania = Column(Integer)
    Kod_pocztowy = Column(String) # czy potrzebny?
    Status_zawodowy = Column(String) 
    Stan_cywilny = Column(String)
    Wyksztalcenie = Column(String) # string czy int
    Plec = Column(Integer) # albo string
    Zrodlo_informacji = Column(String)
    Korzystanie_z_pomocy = Column(JSON)
    Placowka_kierujaca = Column(String)
    Niebieska_karta = Column(Boolean)
    Niebieska_karta_inicjator = Column(String) # warunkowo 
    Grupa_robocza = Column(Boolean) # warunkowo 
    Grupa_robocza_sklad = Column(String) # może lista? jak chcemy analizować tę zmienną? # warunkowo 
    Plan_pomocy = Column(Boolean) # warunkowo 
    Plan_pomocy_opis = Column(String) # warunkowo 
    Narzedzia_prawne = Column(Boolean) # warunkowo 
    Zawiadomienie = Column(Boolean) # warunkowo 
    Postepowanie_cywilne = Column(Boolean)
    Postepowanie_karne = Column(Boolean)
    Postepowanie_rodzinne = Column(Boolean)
    Liczba_dzieci = Column(Integer)
    Problemy = Column(JSON)
    Notatka_diagnoza_sytuacji = Column(String) # do decyzji czy tutaj czy przy wizycie
    Zaproponowane_wsparcie = Column(JSON)
    Ewaluacja = Column(Boolean)
    Status_pacjenta = Column(String) # albo int
    Data_zakonczenia = Column(Date) # do decyzji czy tutaj czy przy wizycie
    

    # zmienne wielokrotnego wyboru - jsony-słowniki: wartość-binarna
    # np tak to by wyglądało dla zaproponowanego wsparcia: {"grupa_wsparcia": 0, "psycholog": 1, "Inne": "jakis string"}
    # dotyczy kolumn: korzystanie z pomocy, problemy, zaproponowane wsparcie

    # zmienne jednokrotnego wyboru, gdzie jest opcja Inne - tabela pomocnicza
    # dotyczy kolumn: źródło informacji, placówka kierująca

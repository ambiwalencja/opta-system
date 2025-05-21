# https://stackoverflow.com/questions/13677781/getting-sqlalchemy-to-issue-create-schema-on-create-all

# https://overiq.com/sqlalchemy-101/defining-schema-in-sqlalchemy-orm/ tutaj spoko opisane budowanie modeli
# https://medium.com/@shubhkarmanrathore/comprehensive-guide-to-schema-design-in-python-with-sqlalchemy-adding-validations-and-constraints-ba40c579a91b tutaj tutek z walidacją danych (np do emaila, telefonu)


from sqlalchemy import Column, Integer, String, DateTime, Date, JSON, Boolean, ForeignKey, MetaData
from db.db_connect import rebase
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import relationship
from user_data import User

ClientDataBase = declarative_base(metadata=MetaData(schema="ClientData"))
# client_metadata = MetaData(schema='ClientData')
# ClientDataBase = declarative_base(metadata=client_metadata)

@rebase
class Pacjent(ClientDataBase):
    __tablename__ = "pacjent"
    ID_pacjenta = Column(Integer, primary_key=True)
    ID_uzytkownika = Column(Integer, ForeignKey(User.ID_uzytkownika)) # osoba rejestrująca
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

    wizyty_indywidualne = relationship("WizytaIndywidualna", back_populates='pacjent')
    uzytkownik = relationship("User", back_populates="pacjenci")
    uczestnik_grupy = relationship('UczestnikGrupy', back_populates='pacjent')

@rebase
class WizytaIndywidualna(ClientDataBase):
    __tablename__ = "wizyta_indywidualna" # to musi być dokładnie ta sama nazwa, co nazwa tabeli, do której chcemy wrzucać dane
    ID_wizyty = Column(Integer, primary_key=True)
    ID_pacjenta = Column(Integer, ForeignKey(Pacjent.ID_pacjenta)) 
    ID_uzytkownika = Column(Integer, ForeignKey(User.ID_uzytkownika))
    Timestamp = Column(DateTime)
    Data = Column(Date) # z tego można wziąć rok, miesiąc
    Specjalista = Column(String) # albo Column(Int) ale moim zdaniem lepiej opisowo
    Liczba_godzin = Column(Integer) # czy potrzebne?
    Notatka_diagnoza_sytuacji = Column(String) # do decyzji czy tutaj czy przy pacjencie
    Notatka_opis_sytuacji = Column(String)
    Notatka_indywidualny_plan = Column(String)
    Notatka_rezultaty = Column(String)
    Notatka_odeslanie_do_innych = Column(String)

    pacjent = relationship('Pacjent', back_populates='wizyty_indywidualne')
    uzytkownik = relationship('User', back_populates='wizyty_indywidualne')

@rebase
class Grupa(ClientDataBase):
    __tablename__ = "grupa" # to musi być dokładnie ta sama nazwa, co nazwa tabeli, do której chcemy wrzucać dane
    ID_grupy = Column(Integer, primary_key=True)
    ID_uzytkownika = Column(Integer, ForeignKey(User.ID_uzytkownika)) # ID użytkownika, który dodał grupę do bazy danych
    Nazwa_grupy = Column(String)
    Timestamp = Column(DateTime) # data dodania?
    Data_rozpoczecia = Column(Date) # ? czy to będzie po prostu data pierwszego spotkania
    Data_zakonczenia = Column(Date) # ? jw - data ostatniego
    Prowadzacy = Column(String) # Lista ID uzytkownikow # TODO: czy to też powinno być jakoś obsłużone w formie foreign keys? tutaj byłaby relacja many to many
    Liczba_godzin = Column(Integer) # czy potrzebne? to może być suma czasu trwania poszczególnych spotkań
    Typ_grupy = Column(String) # warsztat, czy grupa wsparcia, czy trening, etc

    spotkania_grupowe = relationship('Spotkanie_grupowe', back_populates='grupa')
    uzytkownik = relationship('User', back_populates='grupy')


@rebase
class Spotkanie_grupowe(ClientDataBase):
    __tablename__ = "spotkanie_grupowe" # to musi być dokładnie ta sama nazwa, co nazwa tabeli, do której chcemy wrzucać dane
    ID_spotkania = Column(Integer, primary_key=True)
    ID_grupy = Column(Integer, ForeignKey(Grupa.ID_grupy))
    # ID_uzytkownika = Column(Integer, ForeignKey(User.ID_uzytkownika)) # TODO: tak? czy rejestrują je użytkownicy?
    Timestamp = Column(DateTime)
    Data = Column(Date)
    Prowadzacy = Column(String) # ?
    Liczba_godzin = Column(Integer)
    Obecni_uczestnicy = Column(Integer) # lista ID pacjentow
    Notatka_przebieg = Column(String)
    Notatka_rezultaty = Column(String)

    grupa = relationship('Grupa', back_populates='spotkania_grupowe')
    uczestnik_grupy = relationship('UczestnikGrupy', back_populates='grupa')

@rebase
class UczestnikGrupy(ClientDataBase):
    __tablename__ = "uczestnik_grupy"
    ID_uczestnika_grupy = Column(Integer, primary_key=True) # id pary - uczestniko-grupy
    ID_grupy = Column(Integer, ForeignKey(Grupa.ID_grupy))
    ID_pacjenta = Column(Integer, ForeignKey(Pacjent.ID_pacjenta))
    Ukonczenie = Column(Boolean)
    Rezultat = Column(Boolean)

    grupa = relationship('Grupa', back_populates='uczestnik_grupy')
    pacjent = relationship('Pacjent', back_populates='uczestnik_grupy')
    
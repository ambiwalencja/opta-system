from fastapi import HTTPException, status
from datetime import datetime, date
from sqlalchemy import Column, Numeric, func, distinct, Date, Boolean, Integer, desc
# from sqlalchemy.orm import aliased, Query
from sqlalchemy.orm.session import Session
# from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional, Dict, Any, List, Tuple
import json

from db_models.client_data import Pacjent
from db_models.config import PossibleValues

def get_pacjent_counts_by_year(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    pacjent_counts_query = db.query(
        func.extract('year', Pacjent.Data_zgloszenia).cast(Integer).label('year'), 
        func.count(Pacjent.ID_pacjenta).label('count')
        )
    if date_range:
        pacjent_counts_query = pacjent_counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0], 
            Pacjent.Data_zgloszenia <= date_range[1]
            )
    pacjent_counts = pacjent_counts_query.group_by('year').order_by('year').all()
    return {year: count for year, count in pacjent_counts}

def get_sex_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    sex_counts_query = db.query(
        Pacjent.Plec,
        func.count(Pacjent.ID_pacjenta).label('count')
    )
    if date_range:
        sex_counts_query = sex_counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
            )
    sex_counts = sex_counts_query.group_by(Pacjent.Plec).all()
    return {sex: count for sex, count in sex_counts}

def get_average_age_by_year(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[int, float]:
    average_age_query = db.query(
        func.extract('year', Pacjent.Data_zgloszenia).cast(Integer).label('year'),
        func.avg(Pacjent.Wiek).cast(Integer).label('average_age'))
    if date_range:
        average_age_query = average_age_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
        )
    average_age_data = average_age_query.group_by('year').order_by('year').all()
    return {year: average_age for year, average_age in average_age_data}

# TODO: ustalić z mamą jakie przedziały wiekowe mają być
def get_age_group_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    age_groups = {
        '18-25': (18, 25),
        '26-35': (26, 35),
        '36-45': (36, 45),
        '46-55': (46, 55),
        '56-65': (56, 65),
        '66+': (66, 150)
    }
    age_groups_2 = {
        '18-30': (18, 30),
        '31-45': (31, 45),
        '46-60': (46, 60),
        '61+': (61, 150)
    }
    age_group_counts = {}
    for group_name, (age_min, age_max) in age_groups.items():
        query = db.query(func.count(Pacjent.ID_pacjenta))
        if date_range:
            query = query.filter(
                Pacjent.Data_zgloszenia > date_range[0],
                Pacjent.Data_zgloszenia <= date_range[1]
            )
        query = query.filter(Pacjent.Wiek >= age_min, Pacjent.Wiek <= age_max)
        count = query.scalar()
        age_group_counts[group_name] = count
    return age_group_counts

def get_district_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    district_counts_query = db.query(
        Pacjent.Dzielnica,
        func.count(Pacjent.ID_pacjenta).label('count')
    )
    if date_range:
        district_counts_query = district_counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
            )
    district_counts = district_counts_query.group_by(Pacjent.Dzielnica).all()
    return {district: count for district, count in district_counts}

def get_employment_status_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    employment_status_counts_query = db.query(
        Pacjent.Status_zawodowy,
        func.count(Pacjent.ID_pacjenta).label('count')
    )
    if date_range:
        employment_status_counts_query = employment_status_counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
            )
    employment_status_counts = employment_status_counts_query.group_by(Pacjent.Status_zawodowy).all()
    return {status: count for status, count in employment_status_counts}

def get_single_choice_form_variable_counts(db: Session, variable_name: str, date_range: Optional[Tuple[date, date]] = None) -> Dict[Any, int]:
    if not hasattr(Pacjent, variable_name):
        raise ValueError(f"Invalid variable name: {variable_name}")
    variable_column = getattr(Pacjent, variable_name)
    variable_counts_query = db.query(
        variable_column,
        func.count(Pacjent.ID_pacjenta).label('count')
    )
    if date_range:
        variable_counts_query = variable_counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
            )
    variable_counts = variable_counts_query.group_by(variable_column).all()
    return {value: count for value, count in variable_counts}

def get_multiple_choice_form_variable_counts(db: Session, variable_name: str, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:    
    if not hasattr(Pacjent, variable_name):
        raise ValueError(f"Invalid variable name: {variable_name}")
    variable_column = getattr(Pacjent, variable_name) # returns Instrument.column
    all_choices = db.query(PossibleValues.Possible_values).filter(
                PossibleValues.Variable_name == variable_name).scalar() # output is a dict!
    if not all_choices:
        raise ValueError(f"No possible values found for variable: {variable_name}")
    choice_counts = {}
    for choice in all_choices.keys():
        count_query = db.query(func.count(Pacjent.ID_pacjenta)).filter(
            variable_column.contains([choice])
        )
        if date_range:
            count_query = count_query.filter(
                Pacjent.Data_zgloszenia > date_range[0],
                Pacjent.Data_zgloszenia <= date_range[1]
            )
        count = count_query.scalar()
        choice_counts[choice] = count
    return choice_counts
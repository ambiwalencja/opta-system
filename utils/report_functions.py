from fastapi import HTTPException, status
from datetime import datetime, date
from sqlalchemy import Column, Numeric, func, distinct, Date, Boolean, Integer, desc, cast, String
from sqlalchemy.dialects.postgresql import ARRAY
# from sqlalchemy.orm import aliased, Query
from sqlalchemy.orm.session import Session
# from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional, Dict, Any, List, Tuple

from db_models.client_data import Pacjent
from db_models.config import PossibleValues
from utils import report_variables_lists

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

def get_age_group_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    age_groups = {
        '18-25': (18, 25),
        '26-35': (26, 35),
        '36-45': (36, 45),
        '46-55': (46, 55),
        '56+': (56, 150)
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

def get_single_choice_form_variable_counts(db: Session, variable_name: str, date_range: Optional[Tuple[date, date]] = None) -> Dict[Any, int]:
    if not hasattr(Pacjent, variable_name):
        raise ValueError(f"Invalid variable name: {variable_name}")
    if variable_name not in report_variables_lists.single_choice_form_variables:
        raise ValueError(f"Variable {variable_name} is not a single-choice form variable.")
    variable_column = getattr(Pacjent, variable_name)
    variable_counts_query = db.query(
        variable_column,
        func.count(Pacjent.ID_pacjenta).label('count')
    ).filter(variable_column.is_not(None))
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
    if variable_name not in report_variables_lists.multiple_choice_form_variables:
        raise ValueError(f"Variable {variable_name} is not a multiple-choice form variable.")
    variable_column = getattr(Pacjent, variable_name) # returns Instrument.column
    all_choices = db.query(PossibleValues.Possible_values).filter(
                PossibleValues.Variable_name == variable_name).scalar() # output is a dict!
    if not all_choices:
        raise ValueError(f"No possible values found for variable: {variable_name}")
    choice_counts = {}
    for choice in all_choices.keys():
        # count_query = db.query(func.count(Pacjent.ID_pacjenta)).filter(
        count_query = db.query(func.count(variable_column)).filter(
            variable_column.contains([choice])
        )
        if date_range:
            count_query = count_query.filter(
                Pacjent.Data_zgloszenia > date_range[0],
                Pacjent.Data_zgloszenia <= date_range[1]
            )
        count = count_query.scalar()
        choice_counts[choice] = count
        # TODO: dodać sumę wszystkich do słownika
    return choice_counts

def OLD_get_korzystanie_z_pomocy_bool_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[bool, int]:
    counts_query = db.query(func.count(Pacjent.ID_pacjenta))
    if date_range:
        counts_query = counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
        )
    counts_all = counts_query.scalar()
    counts_query = counts_query.filter(Pacjent.Korzystanie_z_pomocy == '["nie korzysta"]')
    counts_nie_korzysta = counts_query.scalar()
    return {"korzysta": counts_all - counts_nie_korzysta, "nie korzysta": counts_nie_korzysta}

def OLD_get_zaproponowane_wsparcie_indywidualne_bool_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    counts_query = db.query(func.count(Pacjent.ID_pacjenta))
    if date_range:
        counts_query = counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
        )
    counts_all = counts_query.scalar()
    counts_offered = counts_query.filter(
        Pacjent.Zaproponowane_wsparcie.op('?|')(cast(report_variables_lists.zaproponowane_wsparcie_indywidualne_options, ARRAY(String)))
        ).scalar()
    return {"zaproponowane": counts_offered, "nie zaproponowane": counts_all - counts_offered}

def get_multiple_choice_variable_as_bool_counts(db: Session, 
                                                variable_name: str, 
                                                list_of_options: List[str],
                                                date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    if not hasattr(Pacjent, variable_name):
        raise ValueError(f"Invalid variable name: {variable_name}")
    variable_column = getattr(Pacjent, variable_name) 
    # counts_query = db.query(func.count(Pacjent.ID_pacjenta))
    counts_query = db.query(func.count(variable_column)) # exclude nulls
    if date_range:
        counts_query = counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
        )
    counts_all = counts_query.scalar()
    counts_selected = counts_query.filter(
        variable_column.op('?|')(cast(list_of_options, ARRAY(String)))
    ).scalar()
    return {True: counts_selected, False: counts_all - counts_selected}

def get_postepowanie_as_bool_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    # counts_query = db.query(func.count(Pacjent.ID_pacjenta))
    counts_query = db.query(func.count(Pacjent.Postepowanie_cywilne)) # zakładam, że nulle są we wszystkich trzech zmiennych w tych samych rekordach
    if date_range:
        counts_query = counts_query.filter(
            Pacjent.Data_zgloszenia > date_range[0],
            Pacjent.Data_zgloszenia <= date_range[1]
        )
    counts_all = counts_query.scalar()
    counts_true = counts_query.filter(
        (Pacjent.Postepowanie_cywilne == True) |
        (Pacjent.Postepowanie_karne == True) |
        (Pacjent.Postepowanie_rodzinne == True)
    ).scalar()
    return {True: counts_true, False: counts_all - counts_true}
from fastapi import HTTPException, status
from datetime import datetime, date
from sqlalchemy import Column, Numeric, func, distinct, Date, Boolean, Integer, desc, cast, String, literal
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.engine.row import Row
# from sqlalchemy.orm import aliased, Query
from sqlalchemy.orm.session import Session
from typing import Optional, Dict, Any, List, Tuple
from collections import defaultdict
import logging


from db_models.client_data import Grupa, Pacjent, SpotkanieGrupowe, UczestnikGrupy, WizytaIndywidualna, obecni_uczestnicy_spotkania
from db_models.config import PossibleValues
from utils import report_variables_lists

logger = logging.getLogger("opta_system_logger")

# TODO: zastanowić się, czy tych powtarzających się fragmentów nie da się ładniej ująć w jednej funkcji, innych funkcjach pomocniczych itp.

def get_pacjent_counts_by_year(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    try:
        logger.info("Getting pacjent counts by year with date_range: %s", str(date_range))
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
        result = {year: count for year, count in pacjent_counts}
        logger.info("Pacjent counts by year retrieved: %d years", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting pacjent counts by year: %s", str(e), exc_info=True)
        raise

def get_average_age_by_year(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[int, float]:
    try:
        logger.info("Getting average age by year with date_range: %s", str(date_range))
        average_age_query = db.query(
            func.extract('year', Pacjent.Data_zgloszenia).cast(Integer).label('year'),
            func.avg(Pacjent.Wiek).cast(Integer).label('average_age'))
        if date_range:
            average_age_query = average_age_query.filter(
                Pacjent.Data_zgloszenia > date_range[0],
                Pacjent.Data_zgloszenia <= date_range[1]
            )
        average_age_data = average_age_query.group_by('year').order_by('year').all()
        result = {year: average_age for year, average_age in average_age_data}
        logger.info("Average age by year retrieved: %d years", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting average age by year: %s", str(e), exc_info=True)
        raise

def get_age_group_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    try:
        logger.info("Getting age group counts with date_range: %s", str(date_range))
        age_group_counts = {}
        for group_name, (age_min, age_max) in report_variables_lists.AGE_GROUPS.items():
            query = db.query(func.count(Pacjent.ID_pacjenta))
            if date_range:
                query = query.filter(
                    Pacjent.Data_zgloszenia > date_range[0],
                    Pacjent.Data_zgloszenia <= date_range[1]
                )
            query = query.filter(Pacjent.Wiek >= age_min, Pacjent.Wiek <= age_max)
            count = query.scalar()
            age_group_counts[group_name] = count
        logger.info("Age group counts retrieved: %d groups", len(age_group_counts))
        return age_group_counts
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting age group counts: %s", str(e), exc_info=True)
        raise

def get_single_choice_form_variable_counts(db: Session, variable_name: str, date_range: Optional[Tuple[date, date]] = None) -> Dict[Any, int]:
    try:
        logger.info("Getting single choice form variable counts for: %s with date_range: %s", variable_name, str(date_range))
        if not hasattr(Pacjent, variable_name):
            logger.warning("Invalid variable name requested: %s", variable_name)
            raise ValueError(f"Invalid variable name: {variable_name}")
        if variable_name not in report_variables_lists.single_choice_fields:
            logger.warning("Variable not a single-choice field: %s", variable_name)
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
        result = {value: count for value, count in variable_counts}
        logger.info("Single choice form variable counts retrieved for %s: %d values", variable_name, len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting single choice form variable counts for %s: %s", variable_name, str(e), exc_info=True)
        raise

def get_multiple_choice_form_variable_counts(db: Session, variable_name: str, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]:
    try:
        logger.info("Getting multiple choice form variable counts for: %s with date_range: %s", variable_name, str(date_range))
        if not hasattr(Pacjent, variable_name):
            logger.warning("Invalid variable name requested: %s", variable_name)
            raise ValueError(f"Invalid variable name: {variable_name}")
        if variable_name not in report_variables_lists.multiple_choice_fields:
            logger.warning("Variable not a multiple-choice field: %s", variable_name)
            raise ValueError(f"Variable {variable_name} is not a multiple-choice form variable.")
        variable_column = getattr(Pacjent, variable_name)
        all_choices = db.query(PossibleValues.Possible_values).filter(
                    PossibleValues.Variable_name == variable_name).scalar()
        if not all_choices:
            logger.warning("No possible values found for variable: %s", variable_name)
            raise ValueError(f"No possible values found for variable: {variable_name}")
        count_query = db.query(func.count(variable_column))
        if date_range:
            count_query = count_query.filter(
                Pacjent.Data_zgloszenia > date_range[0],
                Pacjent.Data_zgloszenia <= date_range[1]
            )
        count_all = count_query.scalar()
        choice_counts = {}
        for choice in all_choices.keys():
            count = count_query.filter(variable_column.contains([choice])).scalar()
            choice_counts[choice] = count
        result = {
            "choices": choice_counts,
            "total": count_all
        }
        logger.info("Multiple choice form variable counts retrieved for %s: %d choices", variable_name, len(choice_counts))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting multiple choice form variable counts for %s: %s", variable_name, str(e), exc_info=True)
        raise


def get_multiple_choice_variable_as_bool_counts(db: Session, 
                                                variable_name: str, 
                                                list_of_options: List[str],
                                                date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    try:
        logger.info("Getting multiple choice variable as bool counts for: %s with date_range: %s", variable_name, str(date_range))
        if not hasattr(Pacjent, variable_name):
            logger.warning("Invalid variable name requested: %s", variable_name)
            raise ValueError(f"Invalid variable name: {variable_name}")
        variable_column = getattr(Pacjent, variable_name)
        counts_query = db.query(func.count(variable_column))
        if date_range:
            counts_query = counts_query.filter(
                Pacjent.Data_zgloszenia > date_range[0],
                Pacjent.Data_zgloszenia <= date_range[1]
            )
        counts_all = counts_query.scalar()
        counts_selected = counts_query.filter(
            variable_column.op('?|')(cast(list_of_options, ARRAY(String)))
        ).scalar()
        result = {True: counts_selected, False: counts_all - counts_selected}
        logger.info("Multiple choice variable as bool counts retrieved for %s", variable_name)
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting multiple choice variable as bool counts for %s: %s", variable_name, str(e), exc_info=True)
        raise

def get_postepowanie_as_bool_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    try:
        logger.info("Getting postepowanie as bool counts with date_range: %s", str(date_range))
        counts_query = db.query(func.count(Pacjent.Postepowanie_cywilne))
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
        result = {True: counts_true, False: counts_all - counts_true}
        logger.info("Postepowanie as bool counts retrieved")
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting postepowanie as bool counts: %s", str(e), exc_info=True)
        raise

def get_wizyty_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    try:
        logger.info("Getting wizyty counts with date_range: %s", str(date_range))
        wizyty_counts_query = db.query(
            func.count(WizytaIndywidualna.ID_wizyty), 
            WizytaIndywidualna.Typ_wizyty.label('typ_wizyty')
            )
        if date_range:
            wizyty_counts_query = wizyty_counts_query.filter(
                WizytaIndywidualna.Data_wizyty > date_range[0], 
                WizytaIndywidualna.Data_wizyty <= date_range[1]
                )
        wizyty_counts = wizyty_counts_query.group_by('typ_wizyty').all()
        result = {typ_wizyty: count for typ_wizyty, count in wizyty_counts}
        logger.info("Wizyty counts retrieved: %d types", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting wizyty counts: %s", str(e), exc_info=True)
        raise

def pacjent_stats_query(db: Session, 
                        column: Column,
                        visit_type: Optional[str] = None,
                        date_range: Optional[Tuple[date, date]] = None)-> List[Row]:
    subquery_stmt = db.query(
        WizytaIndywidualna.ID_pacjenta,
        func.sum(column).label('wizyty_count')
    )
    if date_range:
        subquery_stmt = subquery_stmt.filter(
            WizytaIndywidualna.Data_wizyty > date_range[0],
            WizytaIndywidualna.Data_wizyty <= date_range[1]
        )
    if visit_type:
        subquery_stmt = subquery_stmt.filter(WizytaIndywidualna.Typ_wizyty == visit_type)
    subquery = subquery_stmt.group_by(WizytaIndywidualna.ID_pacjenta).subquery() # tutaj dostajemy liczbę wizyt na pacjenta
    counts = db.query(
        subquery.c.wizyty_count,
        func.count(subquery.c.ID_pacjenta).label('pacjent_count') # sumy pacjentów - przygotowane do grupowania
    ).group_by(subquery.c.wizyty_count).all() # grupujemy po liczbie wizyt; wynik to lista tupli
    return counts
    
def get_pacjent_counts_by_wizyty_number(db: Session, 
                                        visit_type: Optional[str] = None,
                                        date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    try:
        logger.info("Getting pacjent counts by wizyty number (visit_type=%s) with date_range: %s", visit_type, str(date_range))
        counts = pacjent_stats_query(db, column=literal(1), visit_type=visit_type, date_range=date_range)
        result = {label: 0 for label, _ in report_variables_lists.WIZYTY_RANGES}
        for wizyty_count, pacjent_count in counts:
            for label, limit in report_variables_lists.WIZYTY_RANGES:
                if wizyty_count <= limit:
                    result[label] += pacjent_count
                    break
        final_result = {
            "total_pacjenci": sum(result.values()),
            "counts_by_wizyty_number": result
        }
        logger.info("Pacjent counts by wizyty number retrieved: %d total pacjents", final_result["total_pacjenci"])
        return final_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting pacjent counts by wizyty number: %s", str(e), exc_info=True)
        raise

def get_pacjent_counts_by_hours_fixed(db: Session, 
                                visit_type: Optional[str] = None,
                                date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    '''Counts pacjents by total hours of visits, assuming fixed duration per visit type, given in a dictionary.'''
    try:
        logger.info("Getting pacjent counts by hours (fixed) (visit_type=%s) with date_range: %s", visit_type, str(date_range))
        counts = pacjent_stats_query(db, column=literal(1), visit_type=visit_type, date_range=date_range)
        result = {label: 0 for label, _ in report_variables_lists.HOURS_RANGES}
        total_hours = 0
        duration = report_variables_lists.typ_wizyty_options.get(visit_type, 1)
        for wizyty_count, pacjent_count in counts:
            hours_count = wizyty_count * duration
            total_hours += hours_count * pacjent_count
            for label, limit in report_variables_lists.HOURS_RANGES:
                if hours_count <= limit:
                    result[label] += pacjent_count
                    break
        final_result = {
            "total_pacjenci": sum(result.values()),
            "total_hours": total_hours,
            "counts_by_hours": result
        }
        logger.info("Pacjent counts by hours (fixed) retrieved: %d pacjents, %.1f total hours", final_result["total_pacjenci"], final_result["total_hours"])
        return final_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting pacjent counts by hours (fixed): %s", str(e), exc_info=True)
        raise

def get_pacjent_counts_by_hours_dbwise(db: Session, 
                                visit_type: Optional[str] = None,
                                date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    '''Counts pacjents by total hours of visits, using the actual hours recorded in the database.'''
    try:
        logger.info("Getting pacjent counts by hours (dbwise) (visit_type=%s) with date_range: %s", visit_type, str(date_range))
        counts = pacjent_stats_query(db, WizytaIndywidualna.Liczba_godzin, visit_type, date_range)
        result = {label: 0 for label, _ in report_variables_lists.HOURS_RANGES}
        total_hours = 0
        for hours_count, pacjent_count in counts:
            total_hours += hours_count * pacjent_count
            for label, limit in report_variables_lists.HOURS_RANGES:
                if hours_count <= limit:
                    result[label] += pacjent_count
                    break
        final_result = {
            "total_pacjenci": sum(result.values()),
            "total_hours": total_hours,
            "counts_by_hours": result
        }
        logger.info("Pacjent counts by hours (dbwise) retrieved: %d pacjents, %.1f total hours", final_result["total_pacjenci"], final_result["total_hours"])
        return final_result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting pacjent counts by hours (dbwise): %s", str(e), exc_info=True)
        raise


def get_uczestnicy_grupy_counts(db: Session, 
                                date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    try:
        logger.info("Getting uczestnicy grupy counts with date_range: %s", str(date_range))
        uczestnicy_counts_query = db.query(
            UczestnikGrupy.ID_grupy.label('id_grupy'),
            Grupa.Nazwa_grupy.label('nazwa_grupy'),
            func.count(UczestnikGrupy.ID_uczestnika_grupy).label('uczestnicy_count'),
        ).join(Grupa).group_by('id_grupy', 'nazwa_grupy')
        if date_range:
            uczestnicy_counts_query = uczestnicy_counts_query.filter(
                Grupa.Data_rozpoczecia > date_range[0],
                Grupa.Data_rozpoczecia <= date_range[1]
            )
        uczestnicy_counts = uczestnicy_counts_query.all()
        result = {f"{nazwa_grupy} ({id_grupy})": count for id_grupy, nazwa_grupy, count in uczestnicy_counts}
        logger.info("Uczestnicy grupy counts retrieved: %d groups", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting uczestnicy grupy counts: %s", str(e), exc_info=True)
        raise

def get_uczestnicy_grupy_counts_by_completion(db: Session, 
                                date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    try:
        logger.info("Getting uczestnicy grupy counts by completion with date_range: %s", str(date_range))
        uczestnicy_counts_query = db.query(
            Grupa.Nazwa_grupy.label('nazwa_grupy'),
            UczestnikGrupy.Ukonczenie.label('ukonczenie'),
            func.count(UczestnikGrupy.ID_uczestnika_grupy).label('uczestnicy_count')
        ).join(Grupa).group_by(Grupa.Nazwa_grupy, UczestnikGrupy.Ukonczenie)
        if date_range:
            uczestnicy_counts_query = uczestnicy_counts_query.filter(
                Grupa.Data_rozpoczecia > date_range[0],
                Grupa.Data_rozpoczecia <= date_range[1]
            )
        uczestnicy_counts = uczestnicy_counts_query.all()
        nested_result = defaultdict(lambda: {"Total": 0})
        for row in uczestnicy_counts:
            nested_result[row.nazwa_grupy][row.ukonczenie] = row.uczestnicy_count
            nested_result[row.nazwa_grupy]["Total"] += row.uczestnicy_count
        result = dict(nested_result)
        logger.info("Uczestnicy grupy counts by completion retrieved: %d groups", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting uczestnicy grupy counts by completion: %s", str(e), exc_info=True)
        raise

def get_spotkania_grupowe_counts(db: Session,
                                date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    try:
        logger.info("Getting spotkania grupowe counts with date_range: %s", str(date_range))
        spotkania_counts_query = db.query(
            Grupa.ID_grupy.label('grupa_id'),
            func.count(SpotkanieGrupowe.ID_spotkania).label('spotkania_count')
        ).join(Grupa).group_by(Grupa.ID_grupy)
        if date_range:
            spotkania_counts_query = spotkania_counts_query.filter(
                Grupa.Data_rozpoczecia > date_range[0],
                Grupa.Data_rozpoczecia <= date_range[1]
            )
        spotkania_counts = spotkania_counts_query.all()
        result = {id_grupy: count for id_grupy, count in spotkania_counts}
        logger.info("Spotkania grupowe counts retrieved: %d groups", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting spotkania grupowe counts: %s", str(e), exc_info=True)
        raise


def get_uczestnicy_grupy_counts_by_attendance(db: Session,
                                date_range: Optional[Tuple[date, date]] = None) -> Dict[str, Any]:
    try:
        logger.info("Getting uczestnicy grupy counts by attendance with date_range: %s", str(date_range))
        subquery = db.query(
            UczestnikGrupy.ID_uczestnika_grupy.label('uczestnik_id'),
            Grupa.Nazwa_grupy.label('grupa_name'),
            UczestnikGrupy.ID_grupy.label('grupa_id'),
            func.count(obecni_uczestnicy_spotkania.c.ID_spotkania).label('meetings_count')
        ).select_from(UczestnikGrupy
        ).join(Grupa
        ).outerjoin(obecni_uczestnicy_spotkania, UczestnikGrupy.ID_uczestnika_grupy == obecni_uczestnicy_spotkania.c.ID_uczestnika_grupy
        ).outerjoin(SpotkanieGrupowe, obecni_uczestnicy_spotkania.c.ID_spotkania == SpotkanieGrupowe.ID_spotkania)
        if date_range:
            subquery = subquery.filter(
                Grupa.Data_rozpoczecia > date_range[0],
                Grupa.Data_rozpoczecia <= date_range[1]
            )
        subquery = subquery.group_by(
            UczestnikGrupy.ID_uczestnika_grupy, 
            Grupa.Nazwa_grupy,
            UczestnikGrupy.ID_grupy
        ).subquery()
        results = db.query(
            subquery.c.grupa_name,
            subquery.c.grupa_id,
            subquery.c.meetings_count,
            func.count(subquery.c.uczestnik_id).label('uczestnicy_count')
        ).group_by(
            subquery.c.grupa_name,
            subquery.c.grupa_id,
            subquery.c.meetings_count
        ).order_by(
            subquery.c.grupa_name
        ).all()
        meetings_count_by_group_dict = get_spotkania_grupowe_counts(db, date_range)
        nested_result = defaultdict(lambda: {
            "Total_uczestnicy": 0,
            "Total_meetings": 0,
            "Attendance_stats": {label: 0 for label in report_variables_lists.GROUP_ATTENDANCE_RANGES.keys()}
            })
        for row in results:
            grupa_key = f"{row.grupa_name} ({row.grupa_id})"
            nested_result[grupa_key]["Total_uczestnicy"] += row.uczestnicy_count
            nested_result[grupa_key]["Total_meetings"] = meetings_count_by_group_dict.get(row.grupa_id, 0)
            if nested_result[grupa_key]["Total_meetings"] == 0:
                continue
            for label, limit in report_variables_lists.GROUP_ATTENDANCE_RANGES.items():
                if (row.meetings_count / nested_result[grupa_key]["Total_meetings"]) <= limit:
                    nested_result[grupa_key]["Attendance_stats"][label] += row.uczestnicy_count
                    break
        result = dict(nested_result)
        logger.info("Uczestnicy grupy counts by attendance retrieved: %d groups", len(result))
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error getting uczestnicy grupy counts by attendance: %s", str(e), exc_info=True)
        raise
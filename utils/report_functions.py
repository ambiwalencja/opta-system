from fastapi import HTTPException, status
from datetime import datetime, date
from sqlalchemy import Column, func, distinct, Date, Boolean, Integer, desc
# from sqlalchemy.orm import aliased, Query
from sqlalchemy.orm.session import Session
# from fastapi_pagination import Page
from fastapi_pagination.ext.sqlalchemy import paginate
from typing import Optional, Dict, Any, List, Tuple

from db_models.client_data import Pacjent

def get_pacjent_counts_by_year(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[int, int]:
    if not date_range:
        date_range = (date(2016, 1, 1), datetime.now().date())
    pacjent_counts = db.query(
        func.extract('year', Pacjent.Data_zgloszenia).cast(Integer).label('year'), 
        func.count(Pacjent.ID_pacjenta).label('count')
        ).filter(Pacjent.Data_zgloszenia.between(date_range[0], date_range[1])
        ).group_by('year'
        ).order_by('year'
        ).all()
    pacjent_count_dict = {year: count for year, count in pacjent_counts}
    return pacjent_count_dict

def get_plec_counts(db: Session, date_range: Optional[Tuple[date, date]] = None) -> Dict[str, int]:
    if not date_range:
        date_range = (date(2016, 1, 1), datetime.now().date())
    plec_counts = db.query(
        Pacjent.Plec,
        func.count(Pacjent.ID_pacjenta).label('count')
    ).filter(Pacjent.Data_zgloszenia.between(date_range[0], date_range[1])).group_by(Pacjent.Plec).all()
    plec_counts_dict = {plec: count for plec, count in plec_counts}
    return plec_counts_dict
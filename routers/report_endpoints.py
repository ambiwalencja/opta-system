from datetime import date
from sqlalchemy.orm.session import Session
from typing import Optional, List
from fastapi import APIRouter, Depends, HTTPException, status, Query as FastapiQuery

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from db_models.user_data import User
from schemas.user_schemas import UserSignIn
from utils import pacjent_functions, report_functions, report_variables_lists


router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}},
)

@router.get('/pacjent_counts')
def get_pacjent_counts_by_year(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                        start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_pacjent_counts_by_year(db, date_range)

@router.get('/average_age')
def get_average_age_by_year(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_average_age_by_year(db, date_range)

@router.get('/age_groups')
def get_age_group_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    # if current_user.Role != 'admin':
    #     raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_age_group_counts(db, date_range)

@router.get('/pacjent_form_single/')
def get_single_choice_form_variable_counts(variable_name: str = FastapiQuery(..., description="Variable name from pacjent form"),
                       db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_single_choice_form_variable_counts(db, variable_name, date_range)

@router.get('/pacjent_form_single_all/')
def get_all_single_choice_form_variable_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    variable_names = report_variables_lists.single_choice_fields
    result = {}
    for variable_name in variable_names:
        counts = report_functions.get_single_choice_form_variable_counts(db, variable_name, date_range)
        result[variable_name] = counts
    return result

@router.get('/pacjent_form_text_all/')
def get_all_text_form_variable_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    variable_names = report_variables_lists.text_fields
    result = {}
    for variable_name in variable_names:
        counts = report_functions.get_single_choice_form_variable_counts(db, variable_name, date_range)
        result[variable_name] = counts
    return result

@router.get('/pacjent_form_multiple/')
def get_multiple_choice_form_variable_counts(variable_name: str = FastapiQuery(..., description="Variable name from pacjent form"),
                       db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_multiple_choice_form_variable_counts(db, variable_name, date_range)

@router.get('/pacjent_form_multiple_all/')
def get_all_multiple_choice_form_variable_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    variable_names = report_variables_lists.multiple_choice_fields
    result = {}
    for variable_name in variable_names:
        counts = report_functions.get_multiple_choice_form_variable_counts(db, variable_name, date_range)
        result[variable_name] = counts
    return result

@router.get('/pacjent_korzystanie_z_pomocy/')
def get_pacjent_korzystanie_z_pomocy_as_bool(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_multiple_choice_variable_as_bool_counts(db, "Korzystanie_z_pomocy", report_variables_lists.korzystanie_z_pomocy_options, date_range)
    # return report_functions.get_korzystanie_z_pomocy_bool_counts(db, date_range)

@router.get('/pacjent_zaproponowane_wsparcie_indywidualne/')
def get_pacjent_zaproponowane_wsparcie_indywidualne_as_bool(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_multiple_choice_variable_as_bool_counts(db, "Zaproponowane_wsparcie", report_variables_lists.zaproponowane_wsparcie_indywidualne_options, date_range)
    # return report_functions.get_zaproponowane_wsparcie_indywidualne_bool_counts(db, date_range)

@router.get('/pacjent_zaproponowane_wsparcie_grupowe/')
def get_pacjent_zaproponowane_wsparcie_grupowe_as_bool(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_multiple_choice_variable_as_bool_counts(db, "Zaproponowane_wsparcie", report_variables_lists.zaproponowane_wsparcie_grupowe_options, date_range)

@router.get('/pacjent_postepowanie_bool/')
def get_pacjent_postepowanie_bool(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_postepowanie_as_bool_counts(db, date_range)

@router.get('/wizyty_counts')
def get_wizyty_counts(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                        start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_wizyty_counts(db, date_range)

@router.get('/pacjenci_by_wizyty/')
def get_pacjenci_by_wizyty(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       visit_type: Optional[str] = FastapiQuery(None, description="Visit type"),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    return report_functions.get_pacjent_counts_by_wizyty_number(db, visit_type, date_range)

@router.get('/pacjenci_by_wizyty_by_type/')
def get_pacjenci_by_wizyty_by_type(db: Session = Depends(get_db), 
                       current_user: UserSignIn = Depends(get_user_from_token("access_token")),
                       start: Optional[date] = FastapiQuery(None, description="Start date (YYYY-MM-DD)"),
                        end: Optional[date] = FastapiQuery(None, description="End date (YYYY-MM-DD)")):
    if current_user.Role != 'admin':
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    date_range = (start, end) if start and end else None
    visit_type_list = report_variables_lists.typ_wizyty_options
    result = {}
    # result["visit count"] = "number of patients"
    for visit_type in visit_type_list:
        counts = report_functions.get_pacjent_counts_by_wizyty_number(db, visit_type, date_range)
        result[visit_type] = counts
    return result
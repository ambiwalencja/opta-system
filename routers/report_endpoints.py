from sqlalchemy.orm.session import Session
from typing import Optional, List
from fastapi import APIRouter, Body, Depends, HTTPException, status, Query as FastapiQuery
import logging

from db.db_connect import get_db
from auth.oauth2 import get_user_from_token
from db_models.user_data import User
from schemas.user_schemas import UserSignIn
from schemas.report_schemas import DateRangeRequest
from utils import pacjent_functions, report_functions, report_variables_lists

logger = logging.getLogger("opta_system_logger")


router = APIRouter(
    prefix="/report",
    tags=["report"],
    responses={404: {"description": "Not found"}},
)

@router.post('/pacjent_counts')
def get_pacjent_counts_by_year(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_counts report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_counts report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_pacjent_counts_by_year(db, date_range)

@router.post('/average_age')
def get_average_age_by_year(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized average_age report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing average_age report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_average_age_by_year(db, date_range)

@router.post('/age_groups')
def get_age_group_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    logger.info("User %s accessing age_groups report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_age_group_counts(db, date_range)

@router.post('/pacjent_form_single/')
def get_single_choice_form_variable_counts(
    variable_name: str = FastapiQuery(..., description="Variable name from pacjent form"),
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_form_single report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_form_single report for variable: %s", current_user.Username, variable_name)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_single_choice_form_variable_counts(db, variable_name, date_range)

@router.post('/pacjent_form_single_all/')
def get_all_single_choice_form_variable_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_form_single_all report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_form_single_all report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    variable_names = report_variables_lists.single_choice_fields
    result = {}
    for variable_name in variable_names:
        counts = report_functions.get_single_choice_form_variable_counts(db, variable_name, date_range)
        result[variable_name] = counts
    return result

@router.post('/pacjent_form_text_all/')
def get_all_text_form_variable_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    '''No charts here, just a table, cause these are just aggregated text answers.'''
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_form_text_all report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_form_text_all report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    variable_names = report_variables_lists.text_fields
    result = {}
    for variable_name in variable_names:
        counts = report_functions.get_text_variable_counts(db, variable_name, date_range)
        result[variable_name] = counts
    return result

@router.post('/pacjent_form_multiple/')
def get_multiple_choice_form_variable_counts(
    variable_name: str = FastapiQuery(..., description="Variable name from pacjent form"),
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_form_multiple report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_form_multiple report for variable: %s", current_user.Username, variable_name)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_multiple_choice_form_variable_counts(db, variable_name, date_range)

@router.post('/pacjent_form_multiple_all/')
def get_all_multiple_choice_form_variable_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_form_multiple_all report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_form_multiple_all report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    variable_names = report_variables_lists.multiple_choice_fields
    result = {}
    for variable_name in variable_names:
        counts = report_functions.get_multiple_choice_form_variable_counts(db, variable_name, date_range)
        result[variable_name] = counts
    return result

@router.post('/pacjent_korzystanie_z_pomocy/')
def get_pacjent_korzystanie_z_pomocy_as_bool(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_korzystanie_z_pomocy report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_korzystanie_z_pomocy report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_multiple_choice_variable_as_bool_counts(db, "Korzystanie_z_pomocy", report_variables_lists.korzystanie_z_pomocy_options, date_range)

@router.post('/pacjent_zaproponowane_wsparcie_indywidualne/')
def get_pacjent_zaproponowane_wsparcie_indywidualne_as_bool(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_zaproponowane_wsparcie_indywidualne report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_zaproponowane_wsparcie_indywidualne report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_multiple_choice_variable_as_bool_counts(db, "Zaproponowane_wsparcie", report_variables_lists.zaproponowane_wsparcie_indywidualne_options, date_range)

@router.post('/pacjent_zaproponowane_wsparcie_grupowe/')
def get_pacjent_zaproponowane_wsparcie_grupowe_as_bool(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_zaproponowane_wsparcie_grupowe report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_zaproponowane_wsparcie_grupowe report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_multiple_choice_variable_as_bool_counts(db, "Zaproponowane_wsparcie", report_variables_lists.zaproponowane_wsparcie_grupowe_options, date_range)

@router.post('/pacjent_postepowanie_bool/')
def get_pacjent_postepowanie_bool(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjent_postepowanie_bool report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjent_postepowanie_bool report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_postepowanie_as_bool_counts(db, date_range)

@router.post('/wizyty_counts')
def get_wizyty_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized wizyty_counts report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing wizyty_counts report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_wizyty_counts(db, date_range)

@router.post('/pacjenci_by_wizyty/')
def get_pacjenci_by_wizyty(
    visit_type: Optional[str] = FastapiQuery(None, description="Visit type"),
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjenci_by_wizyty report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjenci_by_wizyty report (visit_type=%s)", current_user.Username, visit_type)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_pacjent_counts_by_wizyty_number(db, visit_type, date_range)

@router.post('/pacjenci_by_wizyty_by_type/')
def get_pacjenci_by_wizyty_by_type(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjenci_by_wizyty_by_type report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjenci_by_wizyty_by_type report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    visit_type_list = report_variables_lists.typ_wizyty_options.keys()
    result = {}
    for visit_type in visit_type_list:
        counts = report_functions.get_pacjent_counts_by_wizyty_number(db, visit_type, date_range)
        result[visit_type] = counts
    return result

@router.post('/pacjenci_by_hours/')
def get_pacjenci_by_hours_fixed(
    visit_type: str = FastapiQuery(..., description="Visit type"),
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    '''Hours counted using fixed duration per visit type, given in a dictionary.'''
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjenci_by_hours report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjenci_by_hours report (visit_type=%s)", current_user.Username, visit_type)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_pacjent_counts_by_hours_fixed(db, visit_type, date_range)

@router.post('/pacjenci_by_hours_2/')
def get_pacjenci_by_hours_dbwise(
    visit_type: Optional[str] = FastapiQuery(None, description="Visit type"),
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    '''Hours counted using actual hours recorded in the database.'''
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjenci_by_hours_2 report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjenci_by_hours_2 report (visit_type=%s)", current_user.Username, visit_type)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_pacjent_counts_by_hours_dbwise(db, visit_type, date_range)

@router.post('/pacjenci_by_hours_all/')
def get_pacjenci_by_hours_all_dbwise(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    '''Hours counted using actual hours recorded in the database.'''
    if current_user.Role != 'admin':
        logger.warning("Unauthorized pacjenci_by_hours_all report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing pacjenci_by_hours_all report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    visit_type_list = report_variables_lists.typ_wizyty_options.keys()
    result = {}
    for visit_type in visit_type_list:
        counts = report_functions.get_pacjent_counts_by_hours_dbwise(db, visit_type, date_range)
        result[visit_type] = counts
    return result

@router.post('/uczestnicy_grupy_counts/')
def get_uczestnicy_grupy_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized uczestnicy_grupy_counts report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing uczestnicy_grupy_counts report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_uczestnicy_grupy_counts(db, date_range)

@router.post('/uczestnicy_grupy_completion/')
def get_uczestnicy_grupy_group_completion_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    '''True = ukończone, False = nieukończone, none = brak danych albo grupa trwa'''
    if current_user.Role != 'admin':
        logger.warning("Unauthorized uczestnicy_grupy_completion report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing uczestnicy_grupy_completion report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_uczestnicy_grupy_counts_by_completion(db, date_range)

@router.post('/uczestnicy_grupy_attendance/')
def get_uczestnicy_grupy_attendance_counts(
    request: Optional[DateRangeRequest] = Body(default=None),
    db: Session = Depends(get_db),
    current_user: UserSignIn = Depends(get_user_from_token("access_token")),
):
    if current_user.Role != 'admin':
        logger.warning("Unauthorized uczestnicy_grupy_attendance report request by user: %s", current_user.Username)
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are not an admin")
    logger.info("User %s (admin) accessing uczestnicy_grupy_attendance report", current_user.Username)
    date_range = (request.start, request.end) if request and request.start and request.end else None
    return report_functions.get_uczestnicy_grupy_counts_by_attendance(db, date_range)
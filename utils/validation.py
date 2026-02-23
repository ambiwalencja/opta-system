from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status as http_status
from db_models.config import PossibleValues
from schemas.pacjent_schemas import BaseModel
import logging

logger = logging.getLogger("opta_system_logger")


async def validate_specialist_types(db: Session, specjalista: list[str]) -> None:
    try:
        logger.debug("Validating specialist types: %s", specjalista)
        valid_specialists = db.query(PossibleValues)\
                .filter(PossibleValues.Variable_name == "Specjalista")\
                .first()
            
        if not valid_specialists:
            logger.error("No data found for valid specialist types in database")
            raise HTTPException(
                status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail="Could not validate Specjalista - no data found for valid specialist types"
            )
            
        valid_specialist_types = valid_specialists.Possible_values.keys()
        logger.debug("Valid specialist types: %s", list(valid_specialist_types))
        
        for spec in specjalista:
            if spec not in valid_specialist_types:
                logger.warning("Invalid specialist type provided: %s", spec)
                raise HTTPException(
                    status_code=http_status.HTTP_400_BAD_REQUEST,
                    detail=f"Invalid specialist type: {spec}. Must be one of: {list(valid_specialist_types)}"
                )
        logger.debug("Specialist types validation passed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error validating specialist types: %s", str(e), exc_info=True)
        raise

def validate_choice(db: Session, variable_name: str, chosen_value: str):
    try:
        logger.debug("Validating %s with value: %s", variable_name, chosen_value)
        variable_with_pv = db.query(PossibleValues).filter(PossibleValues.Variable_name == variable_name).first()
        if not variable_with_pv:
            logger.debug("No restriction found for field: %s - skipping validation", variable_name)
            return  # no restriction for this field → skip validation
        
        if chosen_value not in variable_with_pv.Possible_values:  # dict keys are the valid values
            logger.warning("Invalid value '%s' for %s. Allowed values: %s", chosen_value, variable_name, list(variable_with_pv.Possible_values.keys()))
            raise HTTPException(
                status_code=400,
                detail=f"Invalid value '{chosen_value}' for {variable_name}. Allowed: {list(variable_with_pv.Possible_values.keys())}"
            )
        logger.debug("%s validation passed for value: %s", variable_name, chosen_value)
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error validating choice for %s with value %s: %s", variable_name, chosen_value, str(e), exc_info=True)
        raise

def validate_choice_fields(db: Session, data: BaseModel): # zmieniłam z CreatePacjent na BaseModel, żeby można było te przekazać PacjentUpdate0
    try:
        logger.debug("Starting validation of all choice fields")
        data_dict = data.model_dump(by_alias=True, exclude_unset=True)
        
        for field_name, field_value in data_dict.items():
            if field_value is not None:
                # Check for list fields 
                if isinstance(field_value, list):
                    logger.debug("Validating list field %s with %d items", field_name, len(field_value))
                    for item in field_value:
                        validate_choice(db, field_name, item)
                else:
                    validate_choice(db, field_name, field_value)
        logger.debug("All choice fields validation passed")
    except HTTPException:
        raise
    except Exception as e:
        logger.error("Error validating choice fields: %s", str(e), exc_info=True)
        raise
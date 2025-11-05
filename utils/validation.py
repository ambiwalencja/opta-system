from sqlalchemy.orm.session import Session
from fastapi import HTTPException, status as http_status
from db_models.config import PossibleValues
from schemas.pacjent_schemas import BaseModel


async def validate_specialist_types(db: Session, specjalista: list[str]) -> None:
    valid_specialists = db.query(PossibleValues)\
            .filter(PossibleValues.Variable_name == "Specjalista")\
            .first()
        
    if not valid_specialists:
        raise HTTPException(
            status_code=http_status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Could not validate Specjalista - no data found for valid specialist types"
        )
        
    valid_specialist_types = valid_specialists.Possible_values.keys()
    
    for spec in specjalista:
        if spec not in valid_specialist_types:
            raise HTTPException(
                status_code=http_status.HTTP_400_BAD_REQUEST,
                detail=f"Invalid specialist type: {spec}. Must be one of: {list(valid_specialist_types)}"
            )

def validate_choice(db: Session, variable_name: str, chosen_value: str):
    # print(f"Validating {variable_name} with value {chosen_value}")
    variable_with_pv = db.query(PossibleValues).filter(PossibleValues.Variable_name == variable_name).first()
    if not variable_with_pv:
        return  # no restriction for this field → skip validation
    
    if chosen_value not in variable_with_pv.Possible_values:  # dict keys are the valid values
        raise HTTPException(
            status_code=400,
            detail=f"Invalid value '{chosen_value}' for {variable_name}. Allowed: {list(variable_with_pv.Possible_values.keys())}"
        )

def validate_choice_fields(db: Session, data: BaseModel): # zmieniłam z CreatePacjent na BaseModel, żeby można było te przekazać UpdatePacjent
    data_dict = data.model_dump(by_alias=True, exclude_unset=True)
    
    for field_name, field_value in data_dict.items():
        if field_value is not None:
            # Check for list fields 
            if isinstance(field_value, list):
                for item in field_value:
                    validate_choice(db, field_name, item)
            else:
                validate_choice(db, field_name, field_value)
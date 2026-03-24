# Central import point for all database models
# This ensures all models are registered with Base before create_all() is called

from db_models.user_data import User
from db_models.client_data import (
    Pacjent, 
    WizytaIndywidualna, 
    Grupa, 
    UczestnikGrupy, 
    SpotkanieGrupowe,
    pacjent_duplicates,
    prowadzacy_grupy,
    obecni_uczestnicy_spotkania

)
from db_models.config import PossibleValues

__all__ = [
    # User schema models
    'User',
    
    # Client data models
    'Pacjent',
    'WizytaIndywidualna',
    'Grupa',
    'UczestnikGrupy',
    'SpotkanieGrupowe',
    
    # Configuration models
    'PossibleValues',
    
    # Association tables
    'pacjent_duplicates',
    'prowadzacy_grupy',
    'obecni_uczestnicy_spotkania'
]

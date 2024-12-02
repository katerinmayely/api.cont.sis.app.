from pydantic import BaseModel, validator
from typing import Optional
import re

class ActivationValidate(BaseModel):
    code: int
    
    @validator('code')
    def code_validation(cls, value):
        if not isinstance(value, int) or value < 0:
            raise ValueError('Code must be a positive integer')
        return value
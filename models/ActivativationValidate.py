from pydantic import BaseModel, validator
from typing import Optional
import re

class ActivationValidate(BaseModel):
    email: str
    code: int

    @validator('email')
    def email_validation(cls, value):
        if not re.match(r"[^@]+@[^@]+\.[^@]+", value):
            raise ValueError('Invalid email address')

        return value
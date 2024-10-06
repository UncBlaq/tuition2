import re
from typing import Optional
from pydantic import BaseModel, EmailStr

from pydantic import BaseModel, field_validator, ValidationInfo, ConfigDict, Field

class AdminSignUp(BaseModel):

    full_name :str = Field(..., min_length=3, max_length=255)
    email: EmailStr = Field(..., example="admin@example.com")
    password: str = Field(..., min_length=8, example="Strong#Password123")
    confirm_password: str = Field(..., min_length=8, example="Strong#Password123")

    @field_validator('password')
    def validate_password(cls, value):
        if len(value) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r"[A-Z]", value):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r"[a-z]", value):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r"[0-9]", value):
            raise ValueError('Password must contain at least one digit')
        if not re.search(r"[\W_]", value):
            raise ValueError('Password must contain at least one special character')
        return value

    @field_validator('confirm_password')
    def passwords_match(cls, value, info: ValidationInfo):
        password = info.data.get('password')
        if password and value != password:
            raise ValueError('Passwords do not match')
        return value
    
    @field_validator('full_name', 'email')
    def non_empty_strings(cls, value):
        if not value or value.strip() == "":
            raise ValueError('This field cannot be empty')
        return value

class AdminResponse(BaseModel):
    full_name :str
    email: EmailStr 
    is_super_admin : bool


    
    model_config = ConfigDict(
        from_attributes=True
        )


class TokenData(BaseModel):
    email: Optional[str] = None
    

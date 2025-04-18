import re
from datetime import date

from typing import Optional, List, Text, Dict, Any
from pydantic import BaseModel, field_validator, ValidationInfo, ConfigDict, Field, UUID4, Json



class StudentSignUp(BaseModel):

    full_name: str = Field(..., min_length=3, max_length=255)
    email: str = Field(..., min_length=5, max_length=255)
    phone_number: str = Field(..., min_length=10, max_length=20)  # Depends on international phone formats
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)
    field_of_interest: str = Field(..., min_length=3, max_length=255)

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
    
    @field_validator('full_name', 'email', 'phone_number', 'field_of_interest')
    def non_empty_strings(cls, value):
        if not value or value.strip() == "":
            raise ValueError('This field cannot be empty')
        return value

class UpdateProfile(BaseModel):
    bio: Optional[str] = None   
    date_of_birth: Optional[date]  = None
    address: Optional[str] = None

class StudentResponse(BaseModel):
     full_name: str
     email: str
     phone_number: Text
     field_of_interest: str
     is_verified: bool 
     field_of_interest : str

     model_config = ConfigDict(
        from_attributes=True
        )

class Application(BaseModel):
    program_id: UUID4
    custom_field : Optional[Dict[str, Any]] = None 

class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None

class EmailSchema(BaseModel):
       addresses : List[str]


class PasswordResquest(BaseModel):
    email: str

class PasswordResetConfirm(BaseModel):
    new_password: str
    confirm_password: str

    @field_validator('new_password')
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
        new_password = info.data.get('new_password')
        if new_password and value != new_password:
            raise ValueError('Passwords do not match')
        return value
    

class Login(BaseModel):
    email: str
    password: str

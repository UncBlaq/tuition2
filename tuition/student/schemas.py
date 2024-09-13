import re

from typing import Optional, List, Text
from pydantic import BaseModel, field_validator, ValidationInfo, ConfigDict


class StudentSignUp(BaseModel):
    full_name: str
    email: str 
    phone_number: Text 
    password : str
    confirm_password : str 
    field_of_interest : str

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

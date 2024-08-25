import re

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, field_validator, ValidationInfo


class InstitutionSignup(BaseModel):
    name_of_institution : str
    type_of_institution : str
    website : Optional[str]
    address : str
    email : str
    country : str
    official_name : str
    brief_description : str
    password : str
    confirm_password : str
    confirm_password : str

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
    

class InstitutionResponse(BaseModel):
    name_of_institution : str
    type_of_institution : str
    website : str
    address : str
    email : str
    country : str
    official_name : str
    brief_description : str
    is_verified : bool = False


class Token(BaseModel):
    access_token: str
    token_type: str

class TokenData(BaseModel):
    email: Optional[str] = None


class InstitutionBank(BaseModel):
    account_number : str
    bank_name : str
    account_holder_name : str
    country : str
    currency : str
    bank_name : str


class Login(BaseModel):
    email: str
    password: str


# class CreateProgram(BaseModel):
#     name_of_program : str
#     application_deadline : datetime
#     description: str
#     cost
#     image_url: str




import re

from typing import Optional
from pydantic import BaseModel, field_validator, ValidationInfo, ConfigDict, Field, EmailStr


class InstitutionSignup(BaseModel):

    name_of_institution: str = Field(..., min_length=3, max_length=255)
    type_of_institution: str = Field(..., min_length=3, max_length=100)
    website: Optional[str] = Field(None, max_length=255)
    address: str = Field(..., min_length=5, max_length=255)
    email: EmailStr = Field(..., min_length=5, max_length=255)
    country: str = Field(..., min_length=2, max_length=100)
    official_name: str = Field(..., min_length=3, max_length=255)
    brief_description: str = Field(..., min_length=10, max_length=500)
    password: str = Field(..., min_length=8, max_length=100)
    confirm_password: str = Field(..., min_length=8, max_length=100)

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
    
    
    @field_validator('name_of_institution', 'email', 'country')
    def non_empty_strings(cls, value):
        if not value or value.strip() == "":
            raise ValueError('This field cannot be empty')
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
    is_verified : bool = False # Default is False

    
    model_config = ConfigDict(
        from_attributes=True
        )
    
from enum import Enum
from fastapi import HTTPException

class ProgramLevel(str, Enum):
    graduate = "Graduate"
    undergraduate = "Undergraduate"
    postgraduate = "Postgraduate"

class Category(str, Enum):
    arts_and_humanities = "Arts and Humanities"
    business = "Business"
    language_learning = "language learning"
    applied_natural_science = "Applied Natural Science"
    health = "Health"
    information_Technology = "Information Technology"
    math_and_logic = "Math and Logic"
    engineering = "Engineering"
    social_science = "Social Science"
    physical_science = "Physical Science"
    data_science = "Data Science"
    education = "Education"





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

    model_config = ConfigDict(
        from_attributes=True
        )


class Login(BaseModel):
    email: str
    password: str






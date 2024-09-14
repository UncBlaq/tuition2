from decimal import Decimal
import json
from datetime import datetime 
from typing import Annotated
from fastapi import APIRouter, status, BackgroundTasks, Depends, UploadFile, Form

# from fastapi.security import OAuth2PasswordRequestForm

from tuition.institution.schemas import Login, InstitutionSignup, InstitutionResponse, InstitutionBank
from tuition.database import db_dependency
from tuition.institution import crud
from tuition.security.oauth2 import get_current_user


institution_router = APIRouter(
    prefix="/institution",
    tags=["Institution"]
)

@institution_router.post("/signup", response_model= InstitutionResponse, status_code=status.HTTP_201_CREATED)
def sign_up(db: db_dependency, payload: InstitutionSignup, background_tasks: BackgroundTasks):
    """
    ## Creates a institution
    Requires the following
    ```
    name: Name of the institution
    email: Email of the institution
    password: 12-character password
    contact_number: Contact number of the institution
    address: Address of the institution
    description: Description of the institution
    ```
    """
    return crud.sign_up_institution(db, payload, background_tasks)


@institution_router.get('/verify/{token}')
def verify_account(token : str, db :db_dependency):

    """
    ## Verifies the user's account
    Requires the following
    ```
    token : str

    ```
    """

    return crud.verify_user_account(token, db)


@institution_router.post("/add_bank_details", status_code= status.HTTP_201_CREATED)
def add_bank_details(db: db_dependency, payload : InstitutionBank, current_institution : Login = Depends(get_current_user)):
    """
    ## Adds bank details for the institution
    Requires the following         
    ```
    bank_name: Name of the bank
    account_number: Account number of the institution
    account_holder_name: Account holder's name
    account_type: Type of account (Bank Account, Flutterwave Account, etc.)
    ```
    """
    return crud.add_bank_details(db, payload, current_institution)
    

@institution_router.post("/offering/program", status_code= status.HTTP_200_OK)
def create_program(
            db: db_dependency,
            name_of_program: Annotated[str, Form()],
            application_deadline: Annotated[datetime, Form()],
            cost : Annotated[Decimal, Form()],
            description: Annotated[str, Form()],
            image_url: Annotated[str, Form()],
            Image: UploadFile,
            current_institution: Login = Depends(get_current_user)
        ):
    payload = {
        "name_of_program": name_of_program,
        "application_deadline": application_deadline,
        "cost": cost,
        "description": description,
        "image_url": image_url
    }
    
    """
    ## Offers a program for the institution
    Requires the following         
    ```
    title: Title of the program
    description: Description of the program
    course_duration: Duration of the course
    course_price: Price of the course
    course_image: Image of the course
    """
    return crud.create_program(db, payload, Image, current_institution)
    

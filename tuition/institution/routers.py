from decimal import Decimal
from typing import List
from datetime import datetime
from typing import Annotated,Optional, Literal
from fastapi import APIRouter, status, BackgroundTasks, Depends, UploadFile, Form, HTTPException

from tuition.institution.schemas import Login, InstitutionSignup, InstitutionResponse, InstitutionBank, ProgramLevel, Category
from tuition.database import db_dependency
from tuition.institution import crud
from tuition.security.oauth2 import get_current_user

institution_router = APIRouter(
    prefix="/institution",
    tags=["Institution"]
)

@institution_router.post("/signup", response_model= InstitutionResponse, status_code=status.HTTP_201_CREATED)
async def sign_up_institution(db: db_dependency, payload: InstitutionSignup, background_tasks: BackgroundTasks):
    """
    ## Creates a new institution account

    This endpoint registers a new institution in the system by storing its details in the database. It may also trigger background tasks, such as sending a welcome email.

    ### Parameters:
    - **db**: Database session dependency used to interact with the database.
    - **payload**: The institution signup payload containing the required fields:
        - **name_of_institution**: The name of the institution (str) with a minimum length of 3 and a maximum length of 255 characters.
        - **type_of_institution**: The type of institution (str) with a minimum length of 3 and a maximum length of 100 characters.
        - **website**: (Optional) The official website of the institution (str), with a maximum length of 255 characters.
        - **address**: The physical address of the institution (str) with a minimum length of 5 and a maximum length of 255 characters.
        - **email**: The email address of the institution (str), validated as a proper email format, with a minimum length of 5 and a maximum length of 255 characters.
        - **country**: The country where the institution is located (str) with a minimum length of 2 and a maximum length of 100 characters.
        - **official_name**: The official name of the institution (str) with a minimum length of 3 and a maximum length of 255 characters.
        - **brief_description**: A brief description of the institution (str) with a minimum length of 10 and a maximum length of 500 characters.

    - **background_tasks**: A FastAPI BackgroundTasks object used to execute background processes, such as sending a confirmation or welcome email.

    ### Returns:
    - An `InstitutionResponse` object with the details of the newly created institution.

    ### Status Code:
    - **201 Created**: Indicates that the institution account was successfully created.
    """

    return await crud.sign_up_institution(db, payload, background_tasks)


@institution_router.get('/verify/{token}', status_code= status.HTTP_200_OK)
async def verify_account(token : str, db :db_dependency) -> str:

    """
    ## Verifies the institution's account

    This endpoint verifies a institution's account using a provided token. 
    The token is typically a one-time use token sent to the user via email 
    during the registration process.

    **Parameters:**
    - `token` (str): The token sent to the institution's email for account verification.

    **Returns:**
    - (str): A success message indicating the verification status of the account.

    **Responses:**
    - **200 OK**: Returns a success message if the account is verified successfully.
    - **404 Not Found**: If the token is invalid or expired.
    - **422 Unprocessable Entity**: If the token format is incorrect.
    """

    return await crud.verify_user_account(token, db)


@institution_router.post("/add_bank_details", status_code= status.HTTP_201_CREATED)
async def add_bank_details(db: db_dependency, payload : InstitutionBank, current_institution : Login = Depends(get_current_user)):
    """
    ## Adds bank details for the institution

    This endpoint allows institutions to add their bank details. 
    It requires the current institution to be authenticated and provides 
    the necessary bank details in the payload.

    **Parameters:**
    - `db` (db_dependency): The database session dependency.
    - `payload` (InstitutionBank): The bank details to be added, which should include:
        - `account_number` (str): Account number of the institution.
        - `bank_name` (str): Name of the bank.
        - `account_holder_name` (str): Name of the institution's account holder.
        - `country` (str): The country where the bank is located.
        - `currency` (str): The currency associated with the account.

    - `current_institution` (Login): The currently authenticated institution 
      (automatically retrieved from the authentication dependency).

    **Returns:**
    - (str): A success message indicating that the bank details have been added.

    **Responses:**
    - **201 Created**: Indicates that the bank details were added successfully.
    - **400 Bad Request**: If the payload is invalid or missing required fields.
    - **401 Unauthorized**: If the institution is not authenticated.
    - **403 Forbidden**: If the institution does not have permission to add bank details.
    """
    return await crud.add_bank_details(db, payload, current_institution)


@institution_router.post("/offering/program", status_code=status.HTTP_201_CREATED)
async def create_program(
    db: db_dependency,
    name_of_program: Annotated[str, Form()],
    program_level: Annotated[ProgramLevel, Form()],
    categories: Annotated[List[str], Form()],  # Accept a list of strings
    always_available: Annotated[bool, Form()],
    is_free: Annotated[bool, Form()],
    currency_code: Annotated[str, Form(..., min_length=3, max_length=3)],
    description: Annotated[str, Form()],
    image: UploadFile,
    application_deadline: Optional[datetime] = Form(None),
    cost: Optional[Decimal] = Form(None),
    current_institution: Login = Depends(get_current_user)
):
    
    """
    ## Creates a new program offering

    This endpoint allows institutions to create a new program offering. 
    The program details, including its categories and specifications, 
    must be provided in the form data.

    **Parameters:**
    - `db` (db_dependency): The database session dependency.
    - `name_of_program` (str): The name of the program being offered.
    - `program_level` (ProgramLevel): The level of the program (e.g., Undergraduate, Postgraduate).
    - `categories` (List[str]): A list of categories associated with the program, 
      where each category is a string.
    - `always_available` (bool): Indicates if the program is always available for enrollment.
    - `is_free` (bool): Indicates if the program is offered for free.
    - `currency_code` (str): The currency code (3 letters, e.g., USD) for the program's cost.
    - `description` (str): A detailed description of the program.
    - `image` (UploadFile): An image file representing the program.
    - `application_deadline` (Optional[datetime]): The deadline for program applications.
    - `cost` (Optional[Decimal]): The cost of the program.

    - `current_institution` (Login): The currently authenticated institution 
      (automatically retrieved from the authentication dependency).

    **Returns:**
    - (str): A success message indicating that the program has been created.

    **Responses:**
    - **201 Created**: Indicates that the program was created successfully.
    - **400 Bad Request**: If the form data is invalid or required fields are missing, 
      or if an invalid category is provided.
    - **401 Unauthorized**: If the institution is not authenticated.
    - **403 Forbidden**: If the institution does not have permission to create a program.
    """

    # Validate and convert categories
    category_object = []
    for category_str_list in categories:
        category_list = list(category_str_list.split(','))
        for category in category_list:
            try:
                # Try to append the category after converting it to the Enum
                category_object.append(Category(category))

            except ValueError as err:
                # Raise an HTTPException with the error message for the invalid category
                raise HTTPException(
                    status_code=400,
                    detail=f"Invalid category: '{category}'. Error: {err}"
                            )
    payload = {
        "always_available": always_available,
        "name_of_program": name_of_program,
        "application_deadline": application_deadline,
        "cost": cost,
        "is_free": is_free,
        "currency_code": currency_code,
        "description": description,
        "program_level": program_level,
        "categories": category_object
    }

    return await crud.create_program(db, payload, image, current_institution)

@institution_router.post('/event/', status_code=status.HTTP_201_CREATED)
async def create_event(
        db: db_dependency,
        name_of_event: Annotated[str, Form()],
        description: Annotated[str, Form()],
        start_date: Annotated[datetime, Form()],
        end_date: Annotated[datetime, Form()],
        location: Annotated[str, Form()],
        application_deadline : Annotated[datetime, Form()],
        is_online: Annotated[Literal['physical', 'online'], Form()],
        is_free: Annotated[bool, Form()],
        currency_code:  Annotated[str, Form(..., min_length=3, max_length=3)],
        image: UploadFile,
        capacity: Annotated[int, Form()],
        cost : Optional[Decimal] = Form(None),
        current_institution: Login = Depends(get_current_user)
):
    
    """
    ## Creates a new event
    
    This endpoint allows institutions to create a new event.
    The event details, including its location, type, capacity, and specifications, must be provided in the form data.
    
    **Parameters:**
    - `db` (db_dependency): The database session dependency.
    - `name_of_event` (str): The name of the event.
    - `description` (str): A detailed description of the event.
    - `start_date` (datetime): The start date of the event.
    - `end_date` (datetime): The end date of the event.
    - `location` (str): The location of the event.
    - `is_online` (Literal['physical', 'online']): Indicates if the event is online or physical.
    - `is_free` (bool): Indicates if the event is offered for free.
    - `currency_code` (str): The currency code (3 letters, e.g., USD) for the event's cost.
    - `image` (UploadFile): An image file representing the event.
    - `capacity` (str): The capacity of the event.
    
    - `current_institution` (Login): The currently authenticated institution
    **Returns:**
    - (str): A success message indicating that the event has been created.
    
    **Responses:**
    - **201 Created**: Indicates that the event was created successfully.
    - **400 Bad Request**: If the form data is invalid or required fields are missing.
    - **401 Unauthorized**: If the institution is not authenticated.
    - **403 Forbidden**: If the institution does not have permission to create an event.

    """
    payload = {
        "name_of_event": name_of_event,
        "description": description,
        "start_date": start_date,
        "end_date": end_date,
        "location": location,
        "is_online": is_online,
        "is_free": is_free,
        "currency_code": currency_code,
        "capacity": capacity,
        "cost": cost,
        "application_deadline": application_deadline,
    }
    
    return await crud.create_event(db, payload, image, current_institution)
    






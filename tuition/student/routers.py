from typing import List

from fastapi import APIRouter, status, BackgroundTasks, Depends, HTTPException
from pydantic import UUID4

from tuition.student.schemas import StudentSignUp, StudentResponse, PasswordResquest, PasswordResetConfirm, Login, UpdateProfile
from tuition.database import db_dependency
from tuition.student import crud
from tuition.security.oauth2 import get_current_user
import tuition.src_utils as src_utils

student_router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@student_router.post("/signup", response_model= StudentResponse, status_code= status.HTTP_201_CREATED)
async def sign_up_student(db : db_dependency,  payload: StudentSignUp, background_task : BackgroundTasks):

    """
    ## Creates a new student account

    This endpoint is used to register a new student in the system. It saves the student details in the database and triggers background tasks (e.g., sending a welcome email).

    ### Parameters:
    - **db**: Database session dependency used to interact with the database.
    - **payload**: The student signup payload containing the required fields:
        - **full_name**: The student's full name (str).
        - **email**: The student's email address (str).
        - **password**: The student's password (str), which will be hashed before storage.
        - **phone_number**: The student's contact phone number (str).
        - **field_of_interest**: The student's primary field of interest (str).

    - **background_task**: A FastAPI BackgroundTask object used to execute background processes, such as sending a confirmation or welcome email.

    ### Returns:
    - A `StudentResponse` object with the newly created student's details.

    ### Status Code:
    - **201 Created**: Indicates that the student account was successfully created.
    """
    return await crud.sign_up_student(db, payload, background_task)

@student_router.get('/verify/{token}', status_code= status.HTTP_200_OK)
async def verify_student_account(token : str, db :db_dependency):

    """
    ## Verifies a student's account

    This endpoint verifies the student's account using the token sent to the student's email.

    ### Path Parameters:
    - **token**: A unique verification token (str) that was sent to the student's email upon registration. This token is used to confirm the student's email and activate their account.

    ### Parameters:
    - **db**: Database session dependency used to interact with the database for token validation and account verification.

    ### Returns:
    - A 200 OK response indicating successful verification, or raises an error if the token is invalid or expired.
    """

    return await crud.verify_student_account(token, db)


@student_router.post("/password-reset", status_code= status.HTTP_200_OK)
async def reset_password(db : db_dependency, payload : PasswordResquest, background_task :BackgroundTasks):
    """
    ## Sends a password reset link to the user's email

    This endpoint allows users to request a password reset by sending a link to their registered email address. This process is essential for account security and recovery.

    ### Parameters:
    - **db**: Database session dependency used to interact with the database.
    - **payload**: Contains the necessary information for the password reset request:
        - **email**: The email address (str) associated with the user's account to which the password reset link will be sent.

    - **background_task**: A FastAPI BackgroundTasks object used to handle background processes, such as sending the email asynchronously.

    ### Returns:
    - A 200 OK response indicating that the password reset link has been sent successfully to the user's email.
    """
    return await crud.reset_password(db, payload.email, background_task)


@student_router.post('/password-reset-confirm/{token}', status_code= status.HTTP_201_CREATED)
async def confirm_reset_account_password(token : str, payload : PasswordResetConfirm, db :db_dependency):

    """
    ## Confirms the password reset for a user's account

    This endpoint allows users to confirm their password reset request by providing a new password along with a verification token. The token ensures the request is valid and authorized.

    ### Path Parameters:
    - **token**: A unique verification token (str) that was sent to the user's email to authorize the password reset.

    ### Parameters:
    - **payload**: Contains the new password information:
        - **new_password**: The new password (str) that the user wants to set for their account.

    - **db**: Database session dependency used to interact with the database for updating the user's password.

    ### Returns:
    - A 201 Created response indicating that the password has been successfully updated.
    """
    return await crud.confirm_password_reset(token, payload.new_password, db)


@student_router.patch('/update_profile', status_code= status.HTTP_200_OK)

async def update_student_profile(db: db_dependency, payload: UpdateProfile, current_student: Login = Depends(get_current_user)):

    """
    ## Updates a student's profile
    This endpoint allows a student to update their profile information.
    ### Parameters:
    - **db**: Database session dependency to interact with the database.
    - **current_student**: The current logged-in student's credentials.
    - **payload**: The updated student profile information, including the new values for fields like full_name, email, and phone_number.
    ### Returns:
    - A 200 OK response indicating the successful update of the student's profile.
    """
    return await crud.update_student_profile(db, payload, current_student)


@student_router.get("/institions/{page}/{limit}")
async def fetch_institutions(
                            db: db_dependency,
                            page : int = 1,
                            limit : int = 10,
                            current_student: Login = Depends(get_current_user)
                            ):
    """
    ## Fetch all institutions

    This endpoint retrieves all institutions from the database and returns them as a list of `InstitutionResponse` objects.
    ### Parameters:
    - **db**: Database session dependency to interact with the database.
    ### Returns:
    - A list of `InstitutionResponse` objects representing all institutions in the database.
    """

    if page < 1 or limit >= 100:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid page or limit. Page must be greater than 0 and limit must be between 1 and 100."
        )

    return await src_utils.fetch_institutions(db, page, limit, current_student)

@student_router.get('/search/{name}')
async def search_institutions(
                        db: db_dependency, 
                        name : str,
                        page : int = 1, 
                        limit : int = 10,
                        current_student: Login = Depends(get_current_user)
                          ):

     """
    ## Search for institutions by name
    This endpoint searches for institutions by name in the database and returns them as a list of `InstitutionResponse` objects.
    ### Parameters:
    - **db**: Database session dependency to interact with the database.
    - **name**: The name of the institution to search for(Name with strings like).
    ### Returns:
    - A list of `InstitutionResponse` objects representing the institutions that match the search query.
    """
     
     if page < 1 or limit >= 100:
         raise HTTPException(
             status_code=status.HTTP_400_BAD_REQUEST,
             detail="Invalid page or limit. Page must be greater than 0 and limit must be between 1 and 100."
         )
     
     return await  src_utils.search_institution(db, name, page, limit, current_student)
     



@student_router.post("/payments/{program_id}", status_code=status.HTTP_201_CREATED)
async def create_payment(db: db_dependency, program_id: UUID4, current_student: Login = Depends(get_current_user)):
    """
    ## Create a payment for the student

    This endpoint creates a payment request for the student for a specific program. It integrates with the Flutterwave API to generate a payment link.

    ### Parameters:
    - **db**: Database session dependency to interact with the database.
    - **program_id**: UUID of the program the student is paying for.
    - **current_student**: Current authenticated student object retrieved using the login token.

    ### Body Parameters (from `crud.create_payment` function):
    - **amount** (float): The amount to be paid.
    - **description** (str): A brief description of the payment (e.g., "Tuition for Program X").

    ### Integration with Flutterwave:
    - The system interacts with the Flutterwave API by creating a payment request. 
    - It sends the necessary payment details (e.g., amount, description, student info) to Flutterwave.
    - Flutterwave processes the request and returns a **hosted payment URL**.

    ### Returns:
    - A Flutterwave-hosted payment URL that the student can use to complete the payment.
    """
    return await crud.create_payment(db, program_id, current_student)




   


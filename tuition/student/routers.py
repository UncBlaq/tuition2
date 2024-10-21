from fastapi import APIRouter, status, BackgroundTasks, Depends
from pydantic import UUID4

from tuition.student.schemas import StudentSignUp, StudentResponse, PasswordResquest, PasswordResetConfirm, Login
from tuition.database import db_dependency
from tuition.student import crud
from tuition.security.oauth2 import get_current_user

student_router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@student_router.post("/signup", response_model= StudentResponse, status_code= status.HTTP_201_CREATED)
async def sign_up_student(db : db_dependency,  payload: StudentSignUp, background_task : BackgroundTasks):

    """
    ## Creates a student
    Requires the following
    ```
    full_name : str
    email : str
    password : str
    phone_number : str
    field_of_inerest: str
    ```
    """
    return await crud.sign_up_student(db, payload, background_task)

@student_router.get('/verify/{token}', status_code= status.HTTP_200_OK)
async def verify_student_account(token : str, db :db_dependency):

    """
    ## Verifies the user's account
    Requires the following
    ```
    token : str

    ```
    """

    return await crud.verify_student_account(token, db)


@student_router.post("/password-reset", status_code= status.HTTP_200_OK)
async def reset_password(db : db_dependency, payload : PasswordResquest, background_task :BackgroundTasks):
    """
    ## Sends a password reset link to the user's email
    Requires the following
    ```
    email : str
    ```
    """
    return await crud.reset_password(db, payload.email, background_task)


@student_router.post('/password-reset-confirm/{token}', status_code= status.HTTP_201_CREATED)
async def confirm_reset_account_password(token : str, payload : PasswordResetConfirm, db :db_dependency):

    """
    ## Verifies the user's account
    Requires the following
    ```
    token : str

    ```
    """

    return await crud.confirm_password_reset(token, payload.new_password, db)



@student_router.post("/payments", status_code= status.HTTP_201_CREATED)
async def create_payment( db: db_dependency, program_id : UUID4, current_student : Login = Depends(get_current_user)):
    """
    ## Create a payment for the student
    Requires the following
    ```
    amount : float
    description : str
    ```
    """
    return await crud.create_payment(db, program_id, current_student)
   


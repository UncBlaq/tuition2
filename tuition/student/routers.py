from fastapi import APIRouter, status, BackgroundTasks, Depends

from fastapi.security import OAuth2PasswordRequestForm

from tuition.student.schemas import StudentSignUp, StudentResponse, PasswordResquest, PasswordResetConfirm, Login
from tuition.database import db_dependency
from tuition.student import crud
from tuition.security.oauth2 import get_current_user




student_router = APIRouter(
    prefix="/student",
    tags=["Student"]
)


@student_router.get('/verify/{token}')
def verify_user_account(token : str, db :db_dependency):

    """
    ## Verifies the user's account
    Requires the following
    ```
    token : str

    ```
    """

    return crud.verify_user_account(token, db)


@student_router.post('/password-reset-confirm/{token}')
def confirm_reset_account_password(token : str, payload : PasswordResetConfirm, db :db_dependency):

    """
    ## Verifies the user's account
    Requires the following
    ```
    token : str

    ```
    """

    return crud.confirm_password_reset(token, payload.new_password, db)



@student_router.post("/signup", response_model= StudentResponse, status_code= status.HTTP_201_CREATED)
def sign_up(db : db_dependency,  payload: StudentSignUp, background_tasks : BackgroundTasks):

    """
    ## Creates a user
    Requires the following
    ```
    

    ```
    """
    return crud.sign_up(db, payload, background_tasks)



@student_router.post("/password-reset")
def password_reset(db : db_dependency, payload : PasswordResquest, background_task :BackgroundTasks):
    """
    ## Sends a password reset link to the user's email
    Requires the following
    ```
    email : str
    ```
    """
    return crud.password_reset(db, payload.email, background_task)


@student_router.post("/payments")
async def create_payment( db: db_dependency, program_id : int, background_task : BackgroundTasks, current_student : Login = Depends(get_current_user)):
    """
    ## Create a payment for the student
    Requires the following
    ```
    amount : float
    description : str
    ```
    """
    return crud.create_payment(db, program_id, current_student, background_task)
   
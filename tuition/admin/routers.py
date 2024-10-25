from fastapi import APIRouter, status, BackgroundTasks, Depends
from tuition.admin import crud
from tuition.database import db_dependency
from pydantic import UUID4
from tuition.admin.schemas import AdminSignUp
from tuition.security.oauth2 import get_current_user
from tuition.src_utils import Login
from tuition.institution.schemas import Category


admin_router = APIRouter(
    prefix="/admin-user",
    tags=["Admin"]
)

# @admin_router.post("/signup", status_code=status.HTTP_201_CREATED)
# async def sign_up_admin_superuser(db: db_dependency, payload: AdminSignUp):
#     """
#     ## Creates an admin user
#     Requires the following
#     ```
#     name: Name of the admin user
#     email: Email of the admin user
#     password: 12-character password

#     ```
#     """
#     return await crud.sign_up_admin_superUser(db, payload)


@admin_router.post("/admin/create_admin", status_code= status.HTTP_201_CREATED)
async def create_admin(db : db_dependency, payload : AdminSignUp, background_task : BackgroundTasks, current_user : Login = Depends(get_current_user)):
    """
    ## Creates a new admin user

    This endpoint allows a superuser to create a new admin user. 
    The admin's details must be provided in the request payload.

    **Parameters:**
    - `db` (db_dependency): The database session dependency.
    - `payload` (AdminSignUp): The details of the admin user to be created, which should include:
        - `name` (str): Name of the admin user.
        - `email` (str): Email address of the admin user.
        - `password` (str): A password that must be at least 12 characters long.

    - `background_task` (BackgroundTasks): Allows for background task processing (e.g., sending a confirmation email).
    - `current_user` (Login): The currently authenticated superuser 
      (automatically retrieved from the authentication dependency).

    **Returns:**
    - (str): A success message indicating that the admin user has been created.

    **Responses:**
    - **201 Created**: Indicates that the admin user was created successfully.
    - **400 Bad Request**: If the payload is invalid or if the email already exists.
    - **401 Unauthorized**: If the current user is not authenticated as a superuser.
    - **403 Forbidden**: If the current user does not have permission to create an admin user.
    """
    return await crud.sign_up_admin(db, payload, background_task, current_user)


@admin_router.post("/admin/subaccount_id", status_code=status.HTTP_200_OK)
async def add_subaccount_id(db : db_dependency , subaccount_id : str, email : str, current_user : Login = Depends(get_current_user)):
    """
    ## Adds a subaccount ID for the admin

    This endpoint allows an admin to add a subaccount ID associated with their account. 
    The admin must be authenticated to access this endpoint.

    **Parameters:**
    - `db` (db_dependency): The database session dependency.
    - `subaccount_id` (str): The ID of the subaccount to be added.
    - `email` (str): The email address associated with the admin.
    - `current_user` (Login): The currently authenticated admin user 
      (automatically retrieved from the authentication dependency).

    **Returns:**
    - (str): A success message indicating that the subaccount ID has been added.

    **Responses:**
    - **200 OK**: Indicates that the subaccount ID was added successfully.
    - **400 Bad Request**: If the subaccount ID or email is invalid or missing.
    - **401 Unauthorized**: If the current user is not authenticated as an admin.
    - **403 Forbidden**: If the current user does not have permission to add a subaccount ID.
    """
    return await crud.add_subaccount_id(db, current_user, subaccount_id, email)


@admin_router.post("/admin/program_category", status_code=status.HTTP_201_CREATED)
async def add_program_category(db : db_dependency, category : Category, current_user : Login = Depends(get_current_user)):
    """
    ## Adds a program category

    This endpoint allows an admin user to add a new program category to the system. 
    Only authenticated admin users are authorized to access this endpoint.

    **Parameters:**
    - `db` (db_dependency): The database session dependency.
    - `category` (Category): The details of the category to be added, which should include:
        - `name` (str): The name of the category.
        - `description` (str): A brief description of the category.

    - `current_user` (Login): The currently authenticated admin user 
      (automatically retrieved from the authentication dependency).

    **Returns:**
    - (str): A success message indicating that the program category has been added.

    **Responses:**
    - **201 Created**: Indicates that the program category was added successfully.
    - **400 Bad Request**: If the category details are invalid or required fields are missing.
    - **401 Unauthorized**: If the current user is not authenticated as an admin.
    - **403 Forbidden**: If the current user does not have permission to add a program category.
    """
    return await crud.add_program_category(db, category, current_user) 


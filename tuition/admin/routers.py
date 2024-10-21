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
    ## Creates an admin user and it's created by the superuser.
    Requires the following
    ```
    name: Name of the admin user
    email: Email of the admin user
    password: 12-character password

    ```
    """
    return await crud.sign_up_admin(db, payload, background_task, current_user)


@admin_router.post("/admin/subaccount_id", status_code=status.HTTP_200_OK)

async def add_subaccount_id(db : db_dependency , subaccount_id : str, email : str, current_user : Login = Depends(get_current_user)):
    """
    ## Retrieves the admin's subaccount id
    Requires the following
    ```
    admin_id : int
    ```
    """
    return await crud.add_subaccount_id(db, current_user, subaccount_id, email)


@admin_router.post("/admin/program_category", status_code=status.HTTP_201_CREATED)
async def add_program_category(db : db_dependency, category : Category, current_user : Login = Depends(get_current_user)):
    """
    ## Adds a program category and only admin is Authorized
    Requires the following
    ```
    name: Name of the category
    description: Description of the category
    ```
    """
    return await crud.add_program_category(db, category, current_user) 


from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware

from authlib.integrations.starlette_client import OAuth
from tuition.student.routers import student_router
from tuition.student import models as student_models
from tuition.institution import models as institution_models
from tuition.institution.routers import institution_router

from tuition.database import engine, db_dependency
from fastapi.security import OAuth2PasswordRequestForm

from tuition.institution import crud as crud_institution

from tuition.student import crud as crud_student



app = FastAPI(
    title= "Tuition App",
    description="Tuition API"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

student_models.Base.metadata.create_all(bind = engine)
app.include_router(student_router)

institution_models.Base.metadata.create_all(bind = engine)
app.include_router(institution_router)


@app.post("/user/auth/login", tags=["Login"])
def login(db: db_dependency, payload: OAuth2PasswordRequestForm = Depends()):
    """
    ## Logs in an institution
    Requires the following
    ```
    email: Email of the institution
    password: 12-character password
    ```
    """
    return crud_institution.login_institution(db, payload)


@student_router.post("/auth/login", tags=["Login"])
def login(db : db_dependency, payload : OAuth2PasswordRequestForm = Depends()):

    """
    ## Login a user
    Requires the following
    ```
    email : str
    password : str
    ```
    and returns a token pair 'access' 
    """

    return crud_student.login(db, payload)










from fastapi import FastAPI, Depends, HTTPException, status
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
from tuition.student.services import StudentService
from tuition.institution.services import InstitutionService



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


@app.post("/auth/login", tags=["Login"])
def login(db: db_dependency, payload: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user (student or institution)
    """
    student = StudentService.get_student_by_email(db, payload.username)
    if student:
        # Handle student login
        return crud_student.login(db, payload)
    
    institution = InstitutionService.get_institution_by_email(db, payload.username)
    if institution:
        # Handle institution login
        return crud_institution.login_institution(db, payload)

    raise HTTPException(status_code=401, detail="Invalid credentials")













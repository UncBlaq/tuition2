from fastapi import FastAPI, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware

from tuition.student.routers import student_router
from tuition.institution.routers import institution_router
from tuition.admin.routers import admin_router
from tuition.database import engine, db_dependency
from fastapi.security import OAuth2PasswordRequestForm
from tuition.institution import crud as crud_institution
from tuition.student import crud as crud_student
from tuition.admin import crud as admin_crud
import tuition.student.utils as student_utils
import tuition.institution.utils as institution_utils
import tuition.admin.utils as admin_utils

from fastapi import FastAPI
# import sentry_sdk

# sentry_sdk.init(
#     dsn="https://5ae921dea24fec55cca8023da3bbe4c3@o4507693153386496.ingest.de.sentry.io/4507948209143888",
#     # Set traces_sample_rate to 1.0 to capture 100%
#     # of transactions for tracing.
#     traces_sample_rate=1.0,
#     # Set profiles_sample_rate to 1.0 to profile 100%
#     # of sampled transactions.
#     # We recommend adjusting this value in production.
#     profiles_sample_rate=1.0,
# )


app = FastAPI(
    title= "Tuition App",
    description="Tuition API"
)


# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

async def create_db():
    async with engine.begin() as conn:
        from tuition.student import models as student_models
        from tuition.institution import models as institution_models
        from tuition.admin import models as admin_models

        await conn.run_sync(student_models.Base.metadata.create_all)
        await conn.run_sync(institution_models.Base.metadata.create_all)
        await conn.run_sync(admin_models.Base.metadata.create_all)

    await engine.dispose()

@app.on_event("startup")
async def on_startup():
    await create_db()


app.include_router(student_router)

app.include_router(institution_router)

app.include_router(admin_router)

# Add BackGround task to Admin login later
@app.post("/auth/login",status_code=status.HTTP_200_OK, tags=["Login"])
async def login(db: db_dependency, payload: OAuth2PasswordRequestForm = Depends()):
    """
    Logs in a user (student or institution)
    """
    student = await student_utils.get_student_by_email(db, payload.username)
    if student:
        # Handle student login
        return await crud_student.login_student(db, payload)
    
    institution = await institution_utils.get_institution_by_email(db, payload.username)
    if institution:
        # Handle institution login
        return await crud_institution.login_institution(db, payload)
    
    admin = await admin_utils.get_admin_by_email(db, payload.username)
    if admin:
        # Handle admin login
        return await admin_crud.login_admin(db, payload)

    raise HTTPException(status_code=401, detail="Invalid credentials")













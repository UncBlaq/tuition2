from typing import Optional
import random
import string
from fastapi import HTTPException, status, UploadFile
from pydantic import BaseModel
from tuition.security.hash import Hash
import httpx

from supabase import create_client, Client
from tuition.config import Config

from tuition.logger import logger
from tuition.institution.models import Institution, Program
from tuition.institution.schemas import InstitutionResponse
from sqlalchemy.future import select
from tuition.student.utils import get_student_by_email
from tuition.admin.utils import get_admin_by_email
from tuition.student.models import Application

SUPABASE_URL = Config.SUPABASE_URL
SUPABASE_KEY = Config.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class TokenData(BaseModel):
    email: Optional[str] = None

class Login(BaseModel):
    email: str
    password: str



def generate_random_name(length = 10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


#Stopped at program update
async def upload_image_to_supabase(image: UploadFile):
    print("Uploading image")
    image_name = generate_random_name()
    content = await image.read()
    print("Attempting to upload image")

    response = None  # Initialize response 
    response = supabase.storage.from_('alt_bucket').upload(image_name, content)
    if response.status_code == 200:
        print("Image URL:", response.url)
        return f"{SUPABASE_URL}/storage/v1/object/public/alt_bucket/{image_name}"
    
    print({"Image URL":"I returned null response"})
    return None



def verify_password(provided_password: str, hashed_password: str):
    """Verify the provided password against the stored hashed password.

    Args:
        provided_password (str): The password provided by the user during login.
        stored_password (str): The hashed password stored in the database.

    Raises:
        HTTPException: If the provided password does not match the stored password, 
        an exception with status code 401 and a message "Incorrect password" is raised.
    """
    if not Hash.verify(provided_password, hashed_password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect password"
        )
    

def send_payment_request(data, headers):
    url = 'https://api.flutterwave.com/v3/payments'
    response = httpx.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()


async def fetch_institutions(db, page, limit, current_user):
    logger.info(f"Fetching institutions with page {page} and limit {limit}")
    student  = await get_student_by_email(db, current_user.email)
    admin = await get_admin_by_email(db, current_user.email)
    if not student and not admin:
        logger.warning("User does not have permission to access this resource")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to access this resource"
        )

    # Validate the current user
    if student.is_verified == False:
        logger.warning("Student not verified")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student must verify their account before accessing this resource"
        )

    offset = (page - 1) * limit
    
    stmt = select(Institution).order_by(Institution.id.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    institutions = result.scalars().all()
    logger.info(f"Fetched {len(institutions)} institutions")
     # Converts each Institution instance to InstitutionResponse
    institution_responses = [InstitutionResponse.model_validate(inst) for inst in institutions]
    
    return institution_responses


async def search_institution(db, name, page, limit, current_user):

    logger.info(f"Searching institutions by name '{name}' with page {page} and limit {limit}")
    # Validate current_user
    student  = await get_student_by_email(db, current_user.email)
    admin = await get_admin_by_email(db, current_user.email)
    if not student and not admin:
        logger.warning("User does not have permission to access this resource")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User does not have permission to access this resource"
        )

    if student.is_verified == False:
        logger.warning("Student not verified")
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Student must verify their account before accessing this resource"
        )
    
    offset = (page - 1) * limit
    
    stmt = select(Institution).filter(Institution.name_of_institution.ilike(f'%{name}%')).order_by(Institution.id.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    institutions = result.scalars().all()
    logger.info(f"Found {len(institutions)} institutions")
    if len(institutions) == 0:
        return {
            "message" : "No instances were found for the specified name."
        }
    # Converts each Institution instance to InstitutionResponse
    institution_responses = [InstitutionResponse.model_validate(inst) for inst in institutions]
    
    return institution_responses


async def get_program_by_id(db, program_id):
    logger.info(f"Fetching program with id {program_id}")
    stmt = select(Program).filter(Program.id == program_id)
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    program_json = {
            "id": program.id,
            "program_name": program.name_of_program,
            "program_level": program.program_level,
            "always_available": program.always_available,
            "application_deadline": program.application_deadline,
            "cost": program.cost,
            "is_free": program.is_free,
            "currency_code": program.currency_code,
            "description": program.description,
            "institution_id": program.institution_id,
            "subaccount_id": program.subaccount_id,
            "image_url": program.image_url
        }
    return  program_json

async def get_existing_application(db, student_id, program_id):

    logger.info(f"Fetching existing application for student_id {student_id} and program_id {program_id}")
    stmt = select(Application).filter(Application.student_id == student_id).filter(Application.application_type_id == program_id)
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()
    return application


async def get_application_by_id(db, application_id):

    stmt = select(Application).filter(Application.id == application_id)
    result = await db.execute(stmt)
    application = result.scalar_one_or_none()  # Fetches the result or None if not found
    return application





import os

from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from tuition.security.hash import Hash
from tuition.student.models import Student
from tuition.src_utils import send_payment_request
from sqlalchemy.future import select
from tuition.security.jwt import create_access_token, decode_url_safe_token
from tuition.emails_utils import SmtpMailService
import tuition.student.utils as student_utils
import tuition.institution.utils as institution_utils
from tuition.institution.models import Institution
from tuition.institution.schemas import InstitutionResponse
import tuition.admin.utils as admin_utils

from tuition.student.schemas import StudentResponse
from tuition.logger import logger

FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY')

async def sign_up_student(db, payload, background_task):
    logger.info("Creating a new student: %s", payload.email)

    await admin_utils.check_existing_email(db, payload.email)
    await institution_utils.check_existing_email(db, payload.email)
    await student_utils.check_existing_email(db, payload.email)

    hashed_password = Hash.bcrypt(payload.password)
    new_student = student_utils.create_student(payload, hashed_password)

    db.add(new_student)
    await db.commit()
    await db.refresh(new_student)

    smtp_service = SmtpMailService(new_student.email)  
    background_task.add_task(smtp_service.send_verification_email, user = "student")

    logger.info(f"User {new_student.email} has been created")
    return new_student


async def verify_student_account(token, db):
    try:
        # Decode the token
        logger.info("Decoding token for student account verification")
        token_data = decode_url_safe_token(token)
        student_email = token_data.get('email')

        if not student_email:
            logger.warning("Invalid token: email not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Invalid token or email not found in token"
            )

        # Query the database for the student
        logger.info(f"Querying database for student with email: {student_email}")
        stmt = select(Student).filter(Student.email == student_email)
        result = await db.execute(stmt)
        student = result.scalar_one_or_none()
        if not student:
            logger.warning(f"Student with email {student_email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )

        # Create an access token
        access_token = create_access_token(data={"sub": student_email})
        logger.info(f"{student_email} logged in successfully")

        # Update the student's verification status
        student.is_verified = True
        await db.commit()
        logger.info(f"Student {student_email} verified successfully")

        return JSONResponse(
            content={
                "message": "Account Verified Successfully",
                "access_token": access_token,
                "token_type": "bearer"
            },
            status_code=status.HTTP_200_OK
        )

    except Exception as e:
        logger.error(f"An error occurred during account verification: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during account verification"
        )



async def login_student(db, payload):
    logger.info(f"Login attempt for Student: {payload.username}")

    email = payload.username
    student = await student_utils.get_student_by_email(db, email)

    logger.info(f"Student found: {email}")
    student_utils.check_if_verified(student)
    student_object =  StudentResponse.model_validate(student)
    student_utils.verify_password(payload.password, student.hashed_password)
    
    access_token =  create_access_token(data = {
        "sub" : email
    })

    logger.info(f"User {email} logged in successfully")
    return {
        "access_token" : access_token,
        "token_type" : "bearer",
        "student" : student_object
    }


async def reset_password(db, email, background_task):
    try:
        logger.info(f"Attempting to reset password for email: {email}")
        
        student = await student_utils.get_student_by_email(db, email)
        if student is None:
            logger.warning(f"Password reset failed: Student with email {email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        smtp_service = SmtpMailService(student.email) 
        background_task.add_task(smtp_service.send_password_reset_email, user = "student")
        
        logger.info(f"Password reset link sent to email: {email}")
        return JSONResponse(
            content={"message": "Reset link sent to Email"},
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error during password reset for {email}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset"
        )


async def confirm_password_reset(token, new_password, db):
    try:
        logger.info("Attempting to confirm password reset")
        
        # Decode the token
        token_data = decode_url_safe_token(token)
        student_email = token_data.get('email')
        
        if not student_email:

            logger.warning("Invalid token or email missing in token")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Invalid token or email not found in token"
            )
        
        logger.info(f"Querying student by email: {student_email}")
        student = await student_utils.get_student_by_email(db, student_email)
        
        if not student:
            
            logger.warning(f"Student with email {student_email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Reset the password
        new_hash = Hash.bcrypt(new_password)
        student.hashed_password = new_hash
        await db.commit()
        
        logger.info(f"Password reset successfully for {student_email}")
        return JSONResponse(
            content={
                "message": "Password Reset Successfully, Navigate to the login page to login with the new password"
            },
            status_code=status.HTTP_200_OK
        )
        
    except Exception as e:
        logger.error(f"Error during password reset confirmation for {student_email if 'student_email' in locals() else 'unknown'}: {e}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during password reset"
        )
    

async def fetch_institutions(db, page, limit):
    logger.info(f"Fetching institutions with page {page} and limit {limit}")
    offset = (page - 1) * limit
    
    stmt = select(Institution).order_by(Institution.id.desc()).offset(offset).limit(limit)
    result = await db.execute(stmt)
    institutions = result.scalars().all()
    logger.info(f"Fetched {len(institutions)} institutions")
     # Converts each Institution instance to InstitutionResponse
    institution_responses = [InstitutionResponse.model_validate(inst) for inst in institutions]
    
    return institution_responses

async def search_institution(db, name, page, limit):

    logger.info(f"Searching institutions by name '{name}' with page {page} and limit {limit}")
    offset = (page - 1) * limit
    
    stmt = select(Institution).filter(Institution.name_of_institution.ilike(f'%{name}%')).order_by(Institution.id.desc()).offset(offset).limit(limit)

    result = await db.execute(stmt)
    institutions = result.scalars().all()
    logger.info(f"Found {len(institutions)} institutions")
    if len(institutions) == 0:
        return {
            "message" : "No instances were found for the specified name.",
        }
    # Converts each Institution instance to InstitutionResponse
    institution_responses = [InstitutionResponse.model_validate(inst) for inst in institutions]
    
    return institution_responses


async def create_payment(db, program_id, current_student):
    logger.info(f"Creating payment for student********: {current_student.email}")

    student = await student_utils.get_student_by_email(db, current_student.email)
    logger.info(f"Student ALL*****: {student}")
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
  
    program = await institution_utils.get_program_by_id(db, program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")

    subaccount = await institution_utils.get_program_subaccount(db, program.institution_id)  
    if not subaccount:
        raise HTTPException(status_code=404, detail="Subaccount not found")
    
    headers = {
        'Authorization': f'Bearer {FLW_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    
    float_cost = float(program.cost)
    logger.info(f"{subaccount.subaccount_id}")

    data = {
        # "tx_ref": f"TUIT_{student.id}_{uuid.uuid4().hex()}",
        "tx_ref": f"TUIT_{student.id}_{os.urandom(8).hex()}",  # Unique transaction reference
        "amount": float_cost,  # Fetch the amount from the program
        "currency": "NGN",
        "redirect_url": "https://yourplatform.com/payment-success",
        "customer": {
            "email": student.email,
            "name": student.full_name,
            "phonenumber": student.phone_number
        },
        "customizations": {
            "title": program.name_of_program  # Use the program name for the payment title
        },
        "subaccounts": [
            {
                "id": program.subaccount_id  
            }
        ]
    }

    # Add the task to the background tasks
    return send_payment_request(data, headers)






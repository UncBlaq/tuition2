import os
from sqlalchemy.sql import text
from fastapi import HTTPException, status
from fastapi.responses import JSONResponse
from tuition.security.hash import Hash
from tuition.student.models import Student, Application, Transaction
from tuition.src_utils import send_payment_request, get_program_by_id, get_existing_application, get_application_by_id
from sqlalchemy.future import select
from tuition.security.jwt import create_access_token, decode_url_safe_token
from tuition.emails_utils import SmtpMailService
import tuition.student.utils as student_utils
import tuition.institution.utils as institution_utils
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
    
async def update_student_profile(db, payload, current_student):
    logger.info(f"Updating student profile for {current_student.email}")
    
    student = await student_utils.get_student_by_email(db, current_student.email)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    student.bio = payload.bio
    student.date_of_birth = payload.date_of_birth
    student.address = payload.address
    
    await db.commit()
    await db.refresh(student)
    print(student)
    return {
        "message" : "Student profile updated successfully",
        "student" : StudentResponse.model_validate(student)
    }


async def apply_for_program(db, application, current_student):
    logger.info(f"Application for: {application.program_id} for student: {current_student.email}")
    
    student = await student_utils.get_student_by_email(db, current_student.email)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    
    program = await get_program_by_id(db, application.program_id)
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    # Check if the student has already applied for the program
    existing_application = await get_existing_application(db, student.id, application.program_id)
    if existing_application:
        raise HTTPException(status_code=409, detail="Student has already applied for this program")
    
    # Create a new application
    application = Application(
        student_id=student.id,
        application_type_id=application.program_id,
        application_type = "program",
        custom_fields = application.custom_field
    )
    db.add(application)
    await db.commit()
    await db.refresh(application)
    
    return {
        "message" : "Application created successfully",
        "application" : application,
        "program_cost" : program["cost"]
    }


async def create_payment(db, application_id, current_student):
    logger.info(f"Creating payment for student********: {current_student.email}")
    student = await student_utils.get_student_by_email(db, current_student.email)
    if not student:
        raise HTTPException(status_code=404, detail="Student not found")
    application = await get_application_by_id(db, application_id)
    if not application:
        raise HTTPException(status_code=404, detail="Application not found")
    program = await institution_utils.get_program_by_id(db, application.application_type_id)
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
        "tx_ref": f"FLW_{student.id}_{os.urandom(8).hex()}",  # Unique transaction reference
        "amount": float_cost,  # Fetch the amount from the program
        "currency": "NGN",
        "redirect_url": "https://altwavetuition.vercel.app/",
        "customer": {
            "email": student.email,
            "name": student.full_name,
            "phonenumber": student.phone_number
        },
        "customizations": {
            "title": program.name_of_program  
        },
        "subaccounts": [
            {
                "id": program.subaccount_id  
            }
        ]
    }
    new_transaction = Transaction(
        title=program.name_of_program,
        description=f"Payment for {program.name_of_program}",
        payment_method="flutterwave",
        currency=program.currency_code, 
        student_id=student.id,
        institution_id=program.institution_id,
        transaction_type="program_payment",
        amount=program.cost
    )
    db.add(new_transaction)
    await db.commit()
    await db.refresh(new_transaction)

    return send_payment_request(data, headers)

async def get_level_programs(db, level):
    query = text("SELECT * FROM fetch_program(:level)")
    result = await db.execute(query, {"level": level})
    rows = result.fetchall()  # Or use result.mappings().all() if your DB driver supports it

    programs = []
    for r in rows:
        program = {
            "id": r[0],
            "name": r[1],
            "email": r[2]
        }
        programs.append(program)

    return {
        "programs": programs,
        "_links": {
            "self": { "href": f"/programs/{level}" },
            "levels": { "href": "/programs/levels" },
            "enrollments": { "href": "/enrollments" },
            "student": { "href": "/students/me" }
        }
    }
    






import os
import httpx

from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from tuition.security.hash import Hash
from tuition.student.models import Student
from tuition.institution.models import SubAccount
from tuition.security.jwt import create_access_token,  decode_url_safe_token
from tuition.emails import send_verification_email, send_password_reset_email
from tuition.student.services import StudentService
from tuition.institution.services import InstitutionService

from tuition.institution.models import Program

from tuition.student.schemas import StudentResponse
from tuition.logger import logger

FLW_SECRET_KEY = os.getenv('FLW_SECRET_KEY')

def sign_up(db, payload, background_tasks):
    logger.info("Creating a new user: %s", payload.email)

    InstitutionService.check_existing_email(db, payload.email)

    StudentService.check_existing_email(db, payload.email)
    hashed_password = Hash.bcrypt(payload.password)

    new_student = Student(
        full_name = payload.full_name,
        email = payload.email,
        phone_number = payload.phone_number,
        hashed_password = hashed_password,
        field_of_interest = payload.field_of_interest
    )
    db.add(new_student)
    db.commit()
    db.refresh(new_student)

    background_tasks.add_task(send_verification_email, [new_student.email], new_student)

    logger.info(f"User {new_student.email} has been created")
    return new_student



def verify_student_account(token, db):
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
        student = db.query(Student).filter(Student.email == student_email).first()

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
        db.commit()
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



def login(db, payload):
    logger.info(f"Login attempt for user: {payload.username}")

    email = payload.username
    student = StudentService.get_student_by_email(db, email)

    logger.info(f"User found: {email}")
    StudentService.check_if_verified(student)
    student_object = StudentResponse.model_validate(student)
    StudentService.verify_password(payload.password, student.hashed_password)
    
    access_token =  create_access_token(data = {
        "sub" : email
    })

    logger.info(f"User {email} logged in successfully")
    return {
        "access_token" : access_token,
        "token_type" : "bearer",
        "student" : student_object
    }


def password_reset(db, email, background_task):
    try:
        logger.info(f"Attempting to reset password for email: {email}")
        
        student = StudentService.get_student_by_email(db, email)
        if student is None:
            logger.warning(f"Password reset failed: Student with email {email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        logger.info(f"Student {email} found. Sending password reset email")
        background_task.add_task(send_password_reset_email, [email], student)
        
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


def confirm_password_reset(token, new_password, db):
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
        student = db.query(Student).filter(Student.email == student_email).first()
        
        if not student:
            
            logger.warning(f"Student with email {student_email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
        
        # Reset the password
        new_hash = Hash.bcrypt(new_password)
        student.hashed_password = new_hash
        db.commit()
        
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


    

def send_payment_request(data, headers):
    headers = {
        'Authorization': f'Bearer {FLW_SECRET_KEY}',
        'Content-Type': 'application/json'
    }
    url = 'https://api.flutterwave.com/v3/payments'
    response = httpx.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()

def create_payment(db, program_id, current_student, background_tasks):
    # Fetch student data from the database
    student = StudentService.get_student_by_email(db, current_student.email)

    # Fetch the program and its associated subaccount details
    program = db.query(Program).filter(Program.id == program_id).first()
    if not program:
        raise HTTPException(status_code=404, detail="Program not found")
    
    subaccount = db.query(SubAccount).filter(SubAccount.institution_id == program.institution_id).first()
    if not subaccount:
        raise HTTPException(status_code=404, detail="Subaccount not found")
    
    headers = {
        'Authorization': f'Bearer {FLW_SECRET_KEY}',
        'Content-Type': 'application/json'
    }

    data = {
        "tx_ref": f"TUIT_{student.id}_{os.urandom(8).hex()}",  # Unique transaction reference
        "amount": program.cost,  # Fetch the amount from the program
        "currency": "NGN",
        "redirect_url": "https://yourplatform.com/payment-success",
        "customer": {
            "email": student.email,
            "name": student.name,
            "phonenumber": student.phone_number
        },
        "customizations": {
            "title": program.name  # Use the program name for the payment title
        },
        "subaccounts": [
            {
                "id": subaccount.subaccount_id  # Adjust this ratio as needed
            }
        ]
    }

    # Add the task to the background tasks
    background_tasks.add_task(send_payment_request, data, headers)
    return {"message": "Payment is being processed"}


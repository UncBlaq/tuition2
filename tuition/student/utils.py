from fastapi import HTTPException, status
from sqlalchemy.future import select
from tuition.student.models import Student
from tuition.security.hash import Hash


    
async def check_existing_email(db, email: str):
    """Check if an email is already registered in the database.
    
    Args:
        db: The database session.
        email (str): The email address to check.

    Raises:
        HTTPException: If the email is already registered, an exception with 
        status code 400 and a message "Email already exists" is raised.
    """
    stmt = select(Student).filter(Student.email == email)
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()  # Fetches the result or None if not found

    if data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )


async def get_student_by_email(db, username):
    email = username
    stmt = select(Student).filter(Student.email == email)
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()  # Fetches the result or None if not found
    return data



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
    


def check_if_verified(student):
    if not student.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified, check email for verification link"
        )

from tuition.student.models import Student
def create_student(payload, hashed_password):
        new_student = Student(
        full_name = payload.full_name,
        email = payload.email,
        phone_number = payload.phone_number,
        hashed_password = hashed_password,
        field_of_interest = payload.field_of_interest
          )
        return new_student







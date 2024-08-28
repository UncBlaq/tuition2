from fastapi import HTTPException, status
from tuition.student.models import Student
from tuition.security.hash import Hash

class StudentService:

    # @staticmethod
    # def check_invalid_password_len(password):
    #     if len(password) < 6:
    #         raise HTTPException(
    #             status_code=status.HTTP_400_BAD_REQUEST,
    #             detail="Password must be at least 6 characters long")
        
    @staticmethod
    def check_existing_email(db, email: str):
        """Check if an email is already registered in the database.
        
        Args:
            db: The database session.
            email (str): The email address to check.

        Raises:
            HTTPException: If the email is already registered, an exception with 
            status code 400 and a message "Email already exists" is raised.
        """
        db_email = db.query(Student).filter(Student.email == email).first()
        if db_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        

    @staticmethod
    def get_student_by_email(db, username):
        email = username
        return db.query(Student).filter(Student.email == email).first()
    

    @staticmethod
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
        

    @staticmethod
    def check_if_verified(student):
        if not student.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account not verified, check email for verification link"
            )

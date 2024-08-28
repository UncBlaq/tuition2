from fastapi import HTTPException, status
from tuition.institution.models import Institution
from tuition.security.hash import Hash
from tuition.institution.models import SubAccount, Program


class InstitutionService:

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
        db_email = db.query(Institution).filter(Institution.email == email).first()
        if db_email:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Email already exists"
            )
        

    @staticmethod
    def get_institution_by_email(db, username):
        email = username
        institution = db.query(Institution).filter(Institution.email == email).first()
        if not institution:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Invalid credentials"
            )
        return institution
    

    @staticmethod
    def check_if_verified(institution):
        if not institution.is_verified:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="Account not verified, check email for verification link"
            )
        
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

    # Fetches the user from the database based on the current session's user
    def fetch_institution(db, email):
        # Query the database for a user with the same email as the current user
        return db.query(Institution).filter(Institution.email == email).first()
         

    def create_new_bank_details(db, payload, institution_id):
        # institution = db.query(Institution).filter(Institution.email == current_institution.email).first()
        new_bank_details = SubAccount(
            account_number=payload.account_number,
            account_name=payload.account_holder_name,
            bank_name=payload.bank_name,
            institution_id=institution_id,
            country  = payload.country,
            currency = payload.currency
        )
        db.add(new_bank_details)
        db.commit()
        db.refresh(new_bank_details)  # To get the id of the newly created bank_details
        return new_bank_details
    
    def create_new_program(db, payload, institution_id):
        new_program = Program(
                name_of_program=payload['name_of_program'],
                application_deadline=payload['application_deadline'],
                cost = payload['cost'],
                description=payload['description'],
                institution_id=institution_id,
                image_url=payload['image_url'] 
        )
        db.add(new_program)
        db.commit()
        db.refresh(new_program)  # To get the id of the newly created program
        return new_program





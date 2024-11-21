from datetime import datetime, timezone
from fastapi import HTTPException, status
from sqlalchemy.future import select

from tuition.institution.models import Institution
from tuition.institution.schemas import InstitutionBank
from tuition.security.hash import Hash
from tuition.institution.models import SubAccount, Program, program_category_association, Category
from tuition.logger import logger

from sqlalchemy import select
from tuition.institution.models import SubAccount

async def check_existing_email(db, email: str):
    """Check if an email is already registered in the database.
    
    Args:
        db: The database session.
        email (str): The email address to check.

    Raises:
        HTTPException: If the email is already registered, an exception with 
        status code 400 and a message "Email already exists" is raised.
    """
    stmt = select(Institution).filter(Institution.email == email)
    result = await db.execute(stmt)
    db_email = result.scalar_one_or_none()  # Fetches the result or None if not found

    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
async def get_institution_by_email(db, username):
    email = username
    stmt = select(Institution).filter(Institution.email == email)
    result = await db.execute(stmt)
    data = result.scalar_one_or_none()  # Fetches the result or None if not found
    logger.info({
        "all": f"{data}",
        "event": "get_institution_by_email"
    }) 
    return data   

async def get_program_by_id(db, program_id):

    stmt = select(Program).filter(Program.id == program_id)
    result = await db.execute(stmt)
    program = result.scalar_one_or_none()  # Fetches the result or None if not found
    logger.info(f"Program : %s" % program)
    return program


async def get_program_subaccount(db, program_instituition):
    stmt1 = select(SubAccount).filter(SubAccount.institution_id == program_instituition)
    result_sub = await db.execute(stmt1)
    subaccount = result_sub.scalar_one_or_none() 
    return subaccount

def check_if_verified(institution):
    logger.info(f"{institution}")
    if not institution.is_verified:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Account not verified, check email for verification link"
        )
    

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

async def create_new_bank_details(db, payload, institution_id):
    # institution = db.query(Institution).filter(Institution.email == current_institution.email).first()
    new_bank_details = SubAccount(
        account_number=payload.account_number,
        account_name=payload.account_holder_name,
        bank_name=payload.bank_name,
        institution_id=institution_id,
        country  = payload.country,
        currency = payload.currency
    )
    account_object =  InstitutionBank.model_validate(new_bank_details)
    logger.info("Account %s created successfully")
    db.add(new_bank_details)
    await db.commit()
    await db.refresh(new_bank_details) 
    return account_object


async def create_new_program(db, payload, institution_id, subaccount_id):
    new_program = Program(
        name_of_program=payload['name_of_program'],
        program_level=payload['program_level'],
        always_available=payload['always_available'],
        application_deadline=payload['application_deadline'],
        cost=payload['cost'],
        is_free=payload['is_free'],
        currency_code=payload['currency_code'],
        description=payload['description'],
        institution_id=institution_id,
        subaccount_id=subaccount_id,
        image_url=payload['image_url']
    )

    # Step 2: Add the program to the database and commit
    db.add(new_program)
    await db.commit()
    await db.refresh(new_program) 
    print({
        "I don run am" : "Yessssss!!!!!!!",
        "event": new_program
    })

    program_json = {
            "id": new_program.id,
            "program_name": new_program.name_of_program,
            "program_level": new_program.program_level,
            "always_available": new_program.always_available,
            "application_deadline": new_program.application_deadline,
            "cost": new_program.cost,
            "is_free": new_program.is_free,
            "currency_code": new_program.currency_code,
            "description": new_program.description,
            "institution_id": new_program.institution_id,
            "subaccount_id": new_program.subaccount_id,
            "image_url": new_program.image_url
        }
    return   program_json
    # return new_program

async def update_category_program_relation(db, categories, program_id):
    # Prepare a list for bulk insert
    program_category_list = []

    # Loop through the list of categories sent by the client
    for category_name in categories:
        # Query the category based on the name
        category = await db.execute(select(Category).filter_by(name=category_name))
        category_obj = category.scalar_one_or_none()

        if category_obj:
            # For each category, prepare a dictionary of {program_id, category_id}
            program_category_list.append({
                'program_id': program_id,
                'category_id': category_obj.id
            })

    # Ensure that there are categories to insert
    if program_category_list:
        # Bulk insert the associations
        await db.execute(program_category_association.insert().values(program_category_list))

    # Commit the changes to the database
    await db.commit()

async def validate_deadline(application_deadline, always_available):
# If the program is always available, the application deadline must be None
    if always_available:
        if application_deadline is not None:
            raise HTTPException(status_code=400, detail="Application deadline must be NULL for always available programs.")
        return  # No further checks needed

    # If not always available, the application deadline must be set and must be in the future
    if application_deadline is None:
        raise HTTPException(status_code=400, detail="Application deadline is required for non-evergreen programs.")
    
    if application_deadline <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="The application deadline must be in the future.")


async def validate_end_date_deadline(applicaton_deadline, end_date):
    if end_date <= datetime.now(timezone.utc):
        raise HTTPException(status_code=400, detail="The end date must be in the future.")
    
    if applicaton_deadline is not None and applicaton_deadline > end_date:
        raise HTTPException(status_code=400, detail="The application deadline must be earlier than the end date.")
    

async def validate_cost(cost, is_free):
    # If the program is free, the cost must be 0
    if is_free:
        if cost!= 0:
            raise HTTPException(status_code=400, detail="Cost must be 0 for free programs.")
        return  # No further checks needed
    
    # If the program is not free, the cost must be a positive number
    if cost <= 0:
        raise HTTPException(status_code=400, detail="Cost must be a positive number.")
    
from tuition.institution.models import Institution
def create_institution(payload, hashed_password):
    new_institution = Institution(
        name_of_institution = payload.name_of_institution,
        type_of_institution = payload.type_of_institution,
        website = payload.website,
        address = payload.address,
        email = payload.email,
        country = payload.country,
        official_name = payload.official_name,
        brief_description = payload.brief_description,
        hashed_password = hashed_password
    )
    return new_institution


async def get_subaccount_id_by_institution(db, institution_id):

    logger.info(f"{institution_id}get_subaccount_id_by_institution!!!!!!!")
    stmt = select(SubAccount).filter(SubAccount.institution_id == institution_id)
    result = await db.execute(stmt)
    logger.info(f"*****{result}")
    data = result.scalar_one_or_none()  # Returns the subaccount_id or None
    logger.info(f"*****{data}")
    return data









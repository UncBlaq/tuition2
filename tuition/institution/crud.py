from fastapi import HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from tuition.security.hash import Hash
from sqlalchemy.future import select
from tuition.security.jwt import create_access_token, decode_url_safe_token, create_access_token_institution
from tuition.emails_utils import SmtpMailService
from tuition.institution.schemas import InstitutionResponse
from tuition.src_utils import upload_image_to_supabase


from tuition.institution.models import Institution, Event
import tuition.institution.utils as institution_utils
import tuition.student.utils as student_utils
import tuition.admin.utils as admin_utils
from tuition.logger import logger
from concurrent.futures import ThreadPoolExecutor
executor = ThreadPoolExecutor()

async def sign_up_institution(db, payload, background_task):
    logger.info("Creating a new Institution: %s", payload.email)

    await admin_utils.check_existing_email(db, payload.email)
    await student_utils.check_existing_email(db, payload.email)
    await institution_utils.check_existing_email(db, payload.email)

    hashed_password = Hash.bcrypt(payload.password)
    new_institution = institution_utils.create_institution(payload, hashed_password)

    db.add(new_institution)
    await db.commit()
    await db.refresh(new_institution)
    # Send verification email to the new student's email address
    smtp_service = SmtpMailService(new_institution.email)     
    background_task.add_task(smtp_service.send_verification_email, user = "institution")
    
    logger.info(f"Institution {new_institution.email} has been created")
    return new_institution


async def verify_user_account(token, db):
    try:
        # Decode the token
        logger.info("Decoding token for Institution account verification")
        token_data = decode_url_safe_token(token)
        institution_email = token_data.get('email')
        
        if not institution_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Invalid token or email not found in token"
            )
        # Query the database for the student
        logger.info(f"Querying database for Institution with email: {institution_email}")
        stmt = select(Institution).filter(Institution.email == institution_email)
        result = await db.execute(stmt)
        institution = result.scalar_one_or_none()
        if not institution:
            logger.warning(f"Institution with email {institution_email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Institution not found"
            )
                # Create an access token
        access_token = create_access_token(data={"sub": institution_email})

        logger.info(f"{institution_email} logged in successfully")
        # Update the student's verification status
        institution.is_verified = True
        await db.commit()

        logger.info(f"Institution {institution_email} verified successfully")
        return  JSONResponse(
                    content=     {
                        "message": "Account Verified Successfully",
                        "access_token": access_token,
                        "token_type": "bearer"
                        },
                        status_code= status.HTTP_200_OK
                )
    except Exception as e:   
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during account verification"
        )
    
"""
Code base to be edited later for refresh inclussion and avoid hitting db server on every refresh
"""
# async def login_institution(db, payload):
#     logger.info(f"Login attempt for Institution: {payload.username}")

#     email = payload.username
#     institution = await institution_utils.get_institution_by_email(db, email)
    
#     if not institution:
#         logger.warning(f"Institution with email {email} not found")
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="Invalid credentials"
#         )

#     logger.info(f"Institution found***********: {email}")
#     institution_utils.check_if_verified(institution)

#     institution_object = InstitutionResponse.model_validate(institution)
    
#     # Verify the password
#     institution_utils.verify_password(payload.password, institution.hashed_password)
    
#     # Create both access and refresh tokens
#     access_token = create_access_token_institution(data={"sub": email})
#     refresh_token = create_access_token_institution(data={"sub": email}, refresh_token=True)

#     logger.info(f"Institution {email} logged in successfully")
    
#     return {
#         "access_token": access_token["access_token"],
#         "refresh_token": refresh_token["refresh_token"],  # Include the refresh token in the response
#         "token_type": "bearer",
#         "institution": institution_object
#     }


# @router.post("/refresh-token", response_model=Token)
# async def refresh_token(refresh_token: str, db):
#     try:
#         # Decode the refresh token to verify its validity
#         payload = jwt.decode(refresh_token, SECRET_KEY, algorithms=[ALGORITHM])
#         email: str = payload.get("sub")
#         if email is None:
#             raise HTTPException(
#                 status_code=status.HTTP_403_FORBIDDEN,
#                 detail="Invalid refresh token"
#             )
        
#         # Check if the institution still exists in the database
#         institution = await institution_utils.get_institution_by_email(db, email)
#         if not institution:
#             raise HTTPException(
#                 status_code=status.HTTP_404_NOT_FOUND,
#                 detail="Institution not found"
#             )
        
#         # Generate a new access token
#         new_access_token = create_access_token_institution(data={"sub": email})
        
#         return {
#             "access_token": new_access_token["access_token"],
#             "token_type": "bearer"
#         }

#     except JWTError:
#         raise HTTPException(
#             status_code=status.HTTP_403_FORBIDDEN,
#             detail="Invalid refresh token"
#         )

"""
End
"""

async def login_institution(db, payload):
    logger.info(f"Login attempt for Institution: {payload.username}")

    email = payload.username
    institution = await institution_utils.get_institution_by_email(db, email)
    if not institution:
        logger.warning(f"Institution with email {email} not found")
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invalid credentials"
        )

    logger.info(f"Institution found***********: {email}")
    institution_utils.check_if_verified(institution)
    institution_object = InstitutionResponse.model_validate(institution)
    institution_utils.verify_password(payload.password, institution.hashed_password)
    
    access_token =  create_access_token_institution(data = {
        "sub" : email
    })

    logger.info(f"Institution {email} logged in successfully")
    return {
        "access_token" : access_token,
        "token_type" : "bearer",
        "institution" : institution_object
    }


async def add_bank_details(db, payload, current_institution):
    logger.info(f"Bank details upload attempt for Institution: {current_institution.email}")
    institution = await institution_utils.get_institution_by_email(db, current_institution.email)
    if institution is None:
        logger.warning(f"Institution not found: {current_institution.email}")
        raise HTTPException(status_code=404, detail="Institution not found and You do not have access to this endpoint")

 # Check if the institution already has a subaccount
    existing_subaccount = await institution_utils.get_subaccount_id_by_institution(db, institution.id)
    if existing_subaccount:
        logger.warning(f"Subaccount already exists for institution: {institution.email}")
        raise HTTPException(status_code=400, detail="Subaccount already exists, cannot add another.")
    
    logger.info(f"Institution details fetched for: {institution.email}")
    # Log before creating bank details
    logger.info(f"Creating new bank details for institution ID: {institution.id}")
    return await institution_utils.create_new_bank_details(db, payload, institution.id)
    
    
async def create_program(db, payload, Image: UploadFile, current_institution):   
        logger.info(f"Attempting to create a new program for Institution: and payload is : {payload}")

        await institution_utils.validate_deadline(payload["application_deadline"], payload["always_available"])
        await institution_utils.validate_cost(payload['cost'], payload['is_free'])

        #Write a function to validate if program already exists
        logger.info("Validations done!!!")

        institution = await institution_utils.get_institution_by_email(db, current_institution.email)
        if institution is None:
            logger.warning(f"Institution not found: {current_institution.email}")
            raise HTTPException(status_code=404, detail="Institution not found and You do not have access to this endpoint")

        subaccount = await institution_utils.get_subaccount_id_by_institution(db, institution.id)
        if not subaccount:
            logger.warning(f"Subaccount not found for Institution: {current_institution.email}")
            raise HTTPException(status_code=404, detail="Subaccount not found, Add Instition account details before creating a Program")
        #  upload image
        image_url = await upload_image_to_supabase(Image)
        if not image_url:
            raise HTTPException(status_code=500, detail="Image upload failed")
        
        # Now create the program with the image URL
        payload['image_url'] = image_url
        new_program = await institution_utils.create_new_program(db, payload, institution.id, subaccount.subaccount_id)

        await institution_utils.update_category_program_relation(db, payload["categories"], new_program["id"])

        return new_program


async def create_event(db, payload, image, current_institution):
    logger.info(f"Attempting to create a new event for Institution: {current_institution.email}")

    await institution_utils.validate_cost(payload['cost'], payload['is_free'])
    await institution_utils.validate_end_date_deadline(payload['application_deadline'], payload['end_date'])

    institution = await institution_utils.get_institution_by_email(db, current_institution.email)
    if institution is None:
        logger.warning(f"Institution not found: {current_institution.email}")
        raise HTTPException(status_code=404, detail="Institution not found and You do not have access to this endpoint")
    
    subaccount = await institution_utils.get_subaccount_id_by_institution(db, institution.id)
    if not subaccount:
            logger.warning(f"Subaccount not found for Institution: {current_institution.email}")
            raise HTTPException(status_code=404, detail="Subaccount not found, Add Instition account details before creating a Program")
    image_url = await upload_image_to_supabase(image)
    if not image_url:
            raise HTTPException(status_code=500, detail="Image upload failed")
    new_event = Event(
        institution_id=institution.id,
        name_of_event=payload['name_of_event'],
        description=payload['description'],
        start_date=payload['start_date'],
        end_date=payload['end_date'],
        location=payload['location'],
        image_url=image_url,
        capacity=payload['capacity'],
        is_free=payload['is_free'],
        cost=payload['cost'],
        currency_code=payload['currency_code'],
        subaccount_id=subaccount.subaccount_id,
        application_deadline=payload['application_deadline']
    )
    event_json = {
         "event": {
              "name_of_event": new_event.name_of_event,
              "description": new_event.description,
              "start_date": new_event.start_date,
              "end_date": new_event.end_date,
              "location": new_event.location,
              "capacity": new_event.capacity,
              "is_free": new_event.is_free,
              "cost": new_event.cost,
              "currency_code": new_event.currency_code,
              "subaccount_id": new_event.subaccount_id,
              "application_deadline": new_event.application_deadline,
         }
    }

    db.add(new_event)
    await db.commit()
    return event_json




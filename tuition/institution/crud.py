from fastapi import HTTPException, status, UploadFile, File
from fastapi.responses import JSONResponse
from tuition.security.hash import Hash
from tuition.security.jwt import create_access_token, decode_url_safe_token, create_access_token_institution
from tuition.emails import send_verification_email_institution


from tuition.institution.models import Institution, SubAccount
from tuition.institution.services import InstitutionService
from tuition.student.services import StudentService
from tuition.logger import logger

from tuition.config import Config
from supabase import create_client, Client


# from google.cloud import storage

# def upload_to_gcs(bucket_name, source_file_name, destination_blob_name):
#     client = storage.Client()
#     bucket = client.bucket(bucket_name)
#     blob = bucket.blob(destination_blob_name)
#     blob.upload_from_filename(source_file_name)
#     return blob.public_url


# @app.post("/upload-image/")
# async def upload_image(file: UploadFile = File(...)):
#     file_location = f"/tmp/{file.filename}"
#     with open(file_location, "wb+") as file_object:
#         file_object.write(file.file.read())

#     url = upload_to_gcs("your-bucket-name", file_location, file.filename)
#     return {"url": url}



def sign_up_institution(db, payload, background_task):
    logger.info("Creating a new Institution: %s", payload.email)

    StudentService.check_existing_email(db, payload.email)
    
    InstitutionService.check_existing_email(db, payload.email)
    hashed_password = Hash.bcrypt(payload.password)

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
    db.add(new_institution)
    db.commit()
    db.refresh(new_institution)
    
    background_task.add_task(send_verification_email_institution, [new_institution.email], new_institution)
    
    logger.info(f"Institution {new_institution.email} has been created")
    return new_institution


def verify_user_account(token, db):
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
        institution = db.query(Institution).filter(Institution.email == institution_email).first()
        if not institution:

            logger.warning(f"Student with email {institution_email} not found")
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
                # Create an access token
        access_token = create_access_token(data={"sub": institution_email})

        logger.info(f"{institution_email} logged in successfully")
        # Update the student's verification status
        institution.is_verified = True
        db.commit()

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
        # Log the error for debugging (optional)
        # logger.error(f"An error occurred during account verification: {e}")    
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred during account verification"
        )
    

def login_institution(db, payload):
    logger.info(f"Login attempt for Institution: {payload.username}")

    email = payload.username
    institution = InstitutionService.get_institution_by_email(db, email)

    logger.info(f"Institution found: {email}")
    InstitutionService.check_if_verified(institution)
    InstitutionService.verify_password(payload.password, institution.hashed_password)
    
    access_token =  create_access_token_institution(data = {
        "sub" : email
    })

    logger.info(f"Institution {email} logged in successfully")
    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }


def add_bank_details(db, payload, current_institution):

    logger.info(f"Bank details upload attempt for Institution: {current_institution.email}")
    
    # Fetching institution logs
    logger.info(f"Fetching institution details for: {current_institution.email}")
    institution = InstitutionService.fetch_institution(db, current_institution.email)
    
    if not institution:
        logger.warning(f"Institution not found: {current_institution.email}")
        raise HTTPException(status_code=404, detail="Institution not found")
    
    # Log before creating bank details
    logger.info(f"Creating new bank details for institution ID: {institution.id}")
    result = InstitutionService.create_new_bank_details(db, payload, institution.id)
    
    logger.info(f"Bank details successfully created for institution ID: {institution.id}")
    return result




# Supabase credentials
SUPABASE_URL = Config.SUPABASE_URL
SUPABASE_KEY = Config.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)

# @app.post("/upload-file/")
# async def upload_file(file: UploadFile = File(...)):
#     content = await file.read()
#     response = supabase.storage.from_("tuition_image").upload(file.filename, content)
#     if response.status_code == 200:
#         file_url = f"{SUPABASE_URL}/storage/v1/object/public/your-bucket-name/{file.filename}"
#         return {"url": file_url}
#     return {"error": "File upload failed"}


async def upload_image_to_supabase(file: UploadFile):
    content = await file.read()
    response = supabase.storage.from_('your-bucket-name').upload(file.filename, content)
    if response.status_code == 200:
        return f"{SUPABASE_URL}/storage/v1/object/public/your-bucket-name/{file.filename}"
    return None


async def create_program(db, payload, Image: UploadFile, current_institution):
    try:
        # Synchronous fetch (this stays as-is if it's synchronous)
        institution = InstitutionService.fetch_institution(db, current_institution.email)

        if not institution:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Permission denied")

        # Asynchronously upload image
        image_url = await upload_image_to_supabase(Image)

        if not image_url:
            raise HTTPException(status_code=500, detail="Image upload failed")

        # Now create the program with the image URL
        payload['image_url'] = image_url
        return await InstitutionService.create_new_program(db, payload, institution.id)

    except Exception as e:
        logger.error(f"Error occurred: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Program creation failed")


# def create_program(db, payload, Image, current_institution):
#         # Log the attempt to create a program
#     logger.info(f"Attempting to create a new program for Institution: {current_institution.email}")



#     #     # Upload image to cloud storage => Update when my Google Devs account is updated
#     # image_url = cloud_storage_utils.upload_image_to_cloud(image)
#     institution = InstitutionService.fetch_institution(db, current_institution.email)

#     try:
#         # Fetch institution details
#         logger.info(f"Fetching institution details for: {current_institution.email}")
#         institution = InstitutionService.fetch_institution(db, current_institution.email)
        
#         if institution:
#             # Log before creating the program
#             logger.info(f"Creating new program for Institution ID: {institution.id}")
#             return InstitutionService.create_new_program(db, payload, institution.id)
#         else:
#             # Log if the institution is not found
#             logger.warning(f"Institution not found or no permission to create program: {current_institution.email}")
#             raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You do not have permission to create a new program. Contact Support")
    
#     except Exception as e:
#         # Log unexpected errors
#         logger.error(f"An error occurred while creating the program: {e}")
#         raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="An error occurred while creating the program")

  





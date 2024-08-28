from fastapi import HTTPException, status, Depends
from fastapi.responses import JSONResponse
from tuition.security.hash import Hash
from tuition.security.jwt import create_access_token, decode_url_safe_token, create_access_token_institution
from tuition.emails import send_verification_email_institution, send_password_reset_email


from tuition.institution.models import Institution, SubAccount
from tuition.institution.services import InstitutionService
from tuition.student.services import StudentService


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
    return new_institution


def verify_user_account(token, db):
    try:
        # Decode the token
        token_data = decode_url_safe_token(token)
        institution_email = token_data.get('email')
        
        if not institution_email:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND, 
                detail="Invalid token or email not found in token"
            )
        # Query the database for the student
        student = db.query(Institution).filter(Institution.email == institution_email).first()
        if not student:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Student not found"
            )
                # Create an access token
        access_token = create_access_token(data={"sub": institution_email})
        # Update the student's verification status
        student.is_verified = True
        db.commit()
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
    email = payload.username
    institution = InstitutionService.get_institution_by_email(db, email)

    InstitutionService.check_if_verified(institution)
    InstitutionService.verify_password(payload.password, institution.hashed_password)
    
    access_token =  create_access_token_institution(data = {
        "sub" : email
    })
    return {
        "access_token" : access_token,
        "token_type" : "bearer"
    }


def add_bank_details(db, payload, current_institution):
    institution = InstitutionService.fetch_institution(db, current_institution.email)
    return InstitutionService.create_new_bank_details(db, payload, institution.id)



def create_program(db, payload, Image, current_institution):
    #     # Upload image to cloud storage => Update when my Google Devs account is updated
# image_url = cloud_storage_utils.upload_image_to_cloud(image)
    institution = InstitutionService.fetch_institution(db, current_institution.email)
    if institution:
        return InstitutionService.create_new_program(db, payload, institution.id)
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="You do not have permission to to create a new program, Contact Support")
    





    # program = InstitutionService.create_new_program(db, payload, institution.id)
    # return program






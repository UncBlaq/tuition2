from fastapi import HTTPException

from tuition.logger import logger
from tuition.security.hash import Hash
import tuition.institution.utils as institution_utils
import tuition.student.utils as student_utils
import tuition.admin.utils as admin_utils
from tuition.admin.schemas import AdminResponse
from tuition.src_utils import verify_password
from tuition.security.jwt import create_access_token

async def sign_up_admin_superUser(db, payload):
    logger.info("Creating a new admin: %s", payload.email)

    await student_utils.check_existing_email(db, payload.email)
    await institution_utils.check_existing_email(db, payload.email)
    await admin_utils.check_existing_email(db, payload.email)
    logger.info("Email checks completed")

    hashed_password = Hash.bcrypt(payload.password)

    logger.info("Creating Super User!!!!!!!!")
    new_admin = admin_utils.create_admin_super_user(payload, hashed_password)

    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    admin_object = AdminResponse.model_validate(new_admin)

    return admin_object

async def login_admin(db, payload):
    logger.info(f"Login attempt for Admin: {payload.username}")

    email = payload.username
    admin = await admin_utils.get_admin_by_email(db, email)

    logger.info(f"Admin found: {email}")
    admin_object = AdminResponse.model_validate(admin)
    verify_password(payload.password, admin.hashed_password)
    
    access_token =  create_access_token(data = {
        "sub" : email
    })

    logger.info(f"Admin {email} logged in successfully")
    return {
        "access_token" : access_token,
        "token_type" : "bearer",
        "admin" : admin_object
    }



async def sign_up_admin(db, payload, background_task, current_user):
    logger.info("Creating a new admin: %s", payload.email)

    user = await admin_utils.get_admin_by_email(db, current_user.email)
    await admin_utils.check_access_control(user)

    await student_utils.check_existing_email(db, payload.email)
    await institution_utils.check_existing_email(db, payload.email)
    await admin_utils.check_existing_email(db, payload.email)
    logger.info("Email checks completed")

    hashed_password = Hash.bcrypt(payload.password)

    logger.info("Creating Admin!!!!!!!!")
    new_admin = admin_utils.create_admin(payload, hashed_password)

    db.add(new_admin)
    await db.commit()
    await db.refresh(new_admin)
    admin_object = AdminResponse.model_validate(new_admin)

    logger.info(f"Admin {new_admin} created")

    return admin_object


import tuition.institution.utils as institution_utils
async def add_subaccount_id(db, current_user, subaccount_id, email):
    logger.info("Updating subaccount_id by: %s", current_user.email)

    admin_user = await admin_utils.get_admin_by_email(db, current_user.email)
    if not admin_user:
        raise Exception("You are not allowed to access this endpoint.")
    await admin_utils.check_role(admin_user)

    institution = await institution_utils.get_institution_by_email(db, email)
    if not institution:
        raise Exception("Institution not found")
    subaccount = await institution_utils.get_subaccount_id_by_institution(db, institution.id)
    if not subaccount:
        raise Exception("Subaccount not found for the given institution.")

    subaccount.subaccount_id = subaccount_id
    await db.commit()
    await db.refresh(subaccount)
    logger.info(f"Subaccount_id updated for {email}")
    return {
        "subaccount": subaccount,
        "email": email
    }


async def add_program_category(db, category, current_user):
    logger.info("Updating program_category by: %s", current_user.email)
    
    admin_user = await admin_utils.get_admin_by_email(db, current_user.email)
    if not admin_user:
        raise HTTPException(
            status_code=403,
            detail="You are not authorized to access this endpoint."
        )
    await admin_utils.check_if_category_exist(db, category)
    
    await admin_utils.add_program_category(db, category)

    return {
        "message": f"Category successfully added"
    }





    











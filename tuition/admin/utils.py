from fastapi import HTTPException, status
from sqlalchemy.future import select
from tuition.admin.models import Admin
from tuition.institution.models import Category


async def check_existing_email(db, email: str):
    """Check if an email is already registered in the database.
    
    Args:
        db: The database session.
        email (str): The email address to check.

    Raises:
        HTTPException: If the email is already registered, an exception with 
        status code 400 and a message "Email already exists" is raised.
    """
    stmt = select(Admin).filter(Admin.email == email)
    result = await db.execute(stmt)
    db_email = result.scalar_one_or_none()  # Fetches the result or None if not found

    if db_email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already exists"
        )
    
  
from tuition.logger import logger
def create_admin(payload, hashed_password):
        new_admin = Admin(
                full_name = payload.full_name,
                email = payload.email,
                hashed_password = hashed_password,
                )
        logger.info("Admin created")
        return new_admin

# Super admin role is hardcoded for now. In a real-world application, this would be fetched from a database.
# permissions = ["all"]  # Super admin has all permissions by default. In a real-world application, this would be fetched from a database.
# institution_id = payload.institution_id  # Super admin would have access to all institutions by default. In a real-world application, this would be fetched from a database.
# institution_name = payload.institution_name  # Super admin would have access to all institutions by default. In a real-world application, this would be fetched from a database.
# student_id = payload.student_id  # Super admin would have access to all students by default. In a real-world application
def create_admin_super_user(payload, hashed_password):
        new_admin = Admin(
                full_name = payload.full_name,
                email = payload.email,
                hashed_password = hashed_password,
                is_super_admin = True
                )
        logger.info("Super Admin User created")
        return new_admin


async def get_admin_by_email(db, username):
      
    email = username
    stmt = select(Admin).filter(Admin.email == email)
    result = await db.execute(stmt)
    db_email = result.scalar_one_or_none()  # Fetches the result or None if not found
    return db_email


async def check_access_control(user):
    """Check if the user has access to the endpoint.

    Args:
        user (Admin): The admin object.
        endpoint (str): The endpoint being accessed.
        permissions (list): The permissions required for access.

    Raises:
    HTTPException: If the user does not have access to the endpoint, an exception with
    """
    logger.info("Checking permissions")
    if user.is_super_admin:
        logger.info("User %s has access to the endpoint", user.email)
        return 
    raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="Only super users can access this endpoint"
    )

async def check_role(user):
    """Check if the user has access to the endpoint.

    Args:
        user (Admin): The admin object.
        endpoint (str): The endpoint being accessed.
        permissions (list): The permissions required for access.

    Raises:
    HTTPException: If the user does not have access to the endpoint, an exception with
    """
    logger.info("Checking permissions")
    if user.role == 'admin':
        logger.info("User %s has access to the endpoint", user.email)
        return 
    raise HTTPException(
          status_code=status.HTTP_403_FORBIDDEN,
          detail="Only Admin users can access this endpoint"
    )


async def check_if_category_exist(db, category):
     
     stmt = select(Category).filter(Category.name == category)
     result = await db.execute(stmt)
     category_exists = result.scalar_one_or_none()  # Fetches the result or None if not found
     if category_exists:
          logger.info("Category already exists")
          raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Category already exists"
          )
     return

async def add_program_category(db, category):
     
     new_category = Category(name=category)
     db.add(new_category)
     await db.commit()
     await db.refresh(new_category)
     logger.info(f"New category {new_category.name} added successfully")
     
     return new_category.id

import os
from dotenv import load_dotenv

load_dotenv()
from tuition.config import Config
from jose import JWTError, jwt
# from datetime import datetime, timedelta, timezone

import tuition.student.schemas as user_schemas
import tuition.institution.schemas as institution_schemas
# from tuition.student.models import Student

#Takes a string and create a token into it, also time the data is being signed 
from itsdangerous import URLSafeTimedSerializer

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = Config.ALGORITHM
import logging

logging.basicConfig(level=logging.DEBUG)

#Add Expiry later, refresh token
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token

def create_access_token_institution(data: dict):
    to_encode = data.copy()
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token


def verify_token(token : str, credentials_exception):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
        token_data = user_schemas.TokenData(email=email)
        return token_data

    except JWTError:
        raise credentials_exception
    
# def verify_token_institution(token : str, credentials_exception):
#     try:
#         payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
#         username: str = payload.get("sub")
#         if username is None:
#             raise credentials_exception
#         token_data = institution_schemas.TokenData(username=username)
#         return token_data

#     except JWTError:
#         raise credentials_exception



serializer = URLSafeTimedSerializer(
    SECRET_KEY,
    salt="email-Configuration" 
    )


def create_url_safe_token(data : dict):

    return serializer.dumps(data)


def decode_url_safe_token(token : str):
    try:
        token_data = serializer.loads(token)
        return token_data
    
    except Exception as e:
        print("*****decode")
        logging.error(str(e))
     
        


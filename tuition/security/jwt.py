import os
from dotenv import load_dotenv
from datetime import datetime, timedelta

load_dotenv()
from tuition.config import Config
from jose import JWTError, jwt
from tuition.src_utils import TokenData 


#Takes a string and create a token into it, also time the data is being signed 
from itsdangerous import URLSafeTimedSerializer

DATABASE_URL = os.getenv("DATABASE_URL")

SECRET_KEY = os.getenv("SECRET_KEY")
ALGORITHM = Config.ALGORITHM
import logging

logging.basicConfig(level=logging.DEBUG)

ACCESS_TOKEN_EXPIRY = 600
REFRESH_TOKEN_EXPIRY = 86400
#Add Expiry later, refresh token
def create_access_token(data: dict):
    to_encode = data.copy()
    encoded_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_token


"""
Code base to be edited later for refresh inclussion and avoid hitting db server on every refresh
"""

# def create_access_token_institution(data: dict, expiry: timedelta = None, refresh_token: bool = False):
#     to_encode = data.copy()
#     # Access token expiry
#     access_expiry = datetime.now() + (expiry if expiry is not None else timedelta(seconds=ACCESS_TOKEN_EXPIRY))
#     to_encode["exp"] = access_expiry
#     access_token = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

#     # Check if refresh token is requested
#     if refresh_token:
#         refresh_expiry = datetime.now() + timedelta(seconds=REFRESH_TOKEN_EXPIRY)
#         refresh_data = {
#             "sub": to_encode.get("sub"),  # Typically, "sub" represents the subject/user ID
#             "exp": refresh_expiry
#         }
#         refresh_token_value = jwt.encode(refresh_data, SECRET_KEY, algorithm=ALGORITHM)
#         return {"access_token": access_token, "refresh_token": refresh_token_value}

#     return {"access_token": access_token}

"""
End comment
"""


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
        token_data = TokenData(email=email)
        return token_data

    except JWTError:
        raise credentials_exception

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
        logging.error(str(e))
     
        


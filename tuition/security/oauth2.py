from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
import tuition.security.jwt as jwt



# oauth2_scheme_institution = OAuth2PasswordBearer(tokenUrl = "/auth/login")

# def get_current_institution(data : str = Depends(oauth2_scheme_institution)):
#     credentials_exception = HTTPException(
#         status_code=status.HTTP_401_UNAUTHORIZED,
#         detail="Could not validate credentials",
#         headers={"WWW-Authenticate": "Bearer"},
#     )

#     return jwt.verify_token(data, credentials_exception)

oauth2_scheme_student = OAuth2PasswordBearer(tokenUrl = "/user/auth/login")

def get_current_user(data : str = Depends(oauth2_scheme_student)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    return jwt.verify_token(data, credentials_exception)



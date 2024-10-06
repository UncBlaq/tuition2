from typing import Optional
from fastapi import HTTPException, status, UploadFile
from pydantic import BaseModel
from tuition.security.hash import Hash
import httpx

from supabase import create_client, Client
from tuition.config import Config

SUPABASE_URL = Config.SUPABASE_URL
SUPABASE_KEY = Config.SUPABASE_KEY
supabase: Client = create_client(SUPABASE_URL, SUPABASE_KEY)


class TokenData(BaseModel):
    email: Optional[str] = None

class Login(BaseModel):
    email: str
    password: str


async def upload_image_to_supabase(image: UploadFile):
    print("Uploading image")
    content = await image.read()
    print("Image uploaded")
    try:
        response = supabase.storage.from_('alt_bucket').upload(image.filename, content)
        print({
            "message": "Image uploaded successfully",
            "data" : response
        })
        print(response)
        if response.status_code == 200:
            print("Image URL:", response.url)
            return f"{SUPABASE_URL}/storage/v1/object/public/alt_bucket/{image.filename}"
    except Exception as e:
        print("Error uploading image:", str(e))
        # print(response)
        return None

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
    

def send_payment_request(data, headers):
    url = 'https://api.flutterwave.com/v3/payments'
    response = httpx.post(url, json=data, headers=headers)
    response.raise_for_status()
    return response.json()
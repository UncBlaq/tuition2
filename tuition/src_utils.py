from typing import Optional
import random
import string
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




def generate_random_name(length = 10):
    letters = string.ascii_letters + string.digits
    return ''.join(random.choice(letters) for i in range(length))


#Stopped at program update
async def upload_image_to_supabase(image: UploadFile):
    print("Uploading image")
    image_name = generate_random_name()
    content = await image.read()
    print("Attempting to upload image")

    response = None  # Initialize response 
    response = supabase.storage.from_('alt_bucket').upload(image_name, content)
    if response.status_code == 200:
        print("Image URL:", response.url)
        return f"{SUPABASE_URL}/storage/v1/object/public/alt_bucket/{image_name}"
    
    print({"Image URL":"I returned null response"})
    return None


    # try:
    #     response = supabase.storage.from_('alt_bucket').upload(image_name, content)
    #     print({
    #         "message": "Image uploaded successfully",
    #         "data": response
    #     })
    #     if response.status_code == 200:
    #         print("Image URL:", response.url)
    #         return f"{SUPABASE_URL}/storage/v1/object/public/alt_bucket/{image_name}"
    # except Exception as e:
    #     print("Error uploading image:", str(e))
    #     if response is not None:
    #         print(response)  # If 'response' was set before the error, print it.
    #     return None


# async def upload_image_to_supabase(image: UploadFile):
#     print("Uploading image")
#     image_name = generate_random_name()
#     # image.filename = image_name
#     content = await image.read()
#     print("Image uploaded")
#     response = None
#     try:
#         response = supabase.storage.from_('alt_bucket').upload(image_name, content)
#         print({
#             "message": "Image uploaded successfully",
#             "data" : response
#         })
#         print(response)
#         if response.status_code == 200:
#             print("Image URL:", response.url)
#             return f"{SUPABASE_URL}/storage/v1/object/public/alt_bucket/{image_name}"
#     except Exception as e:
#         print("Error uploading image:", str(e))
#         # print(response)
#         return None

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
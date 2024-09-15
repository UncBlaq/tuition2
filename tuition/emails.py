import os
from typing import List

from fastapi import HTTPException, status
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema, MessageType

from pathlib import Path
from tuition.config import Config

import logging
logging.basicConfig(level= logging.DEBUG)
logger = logging.getLogger(__name__)
from tuition.security.jwt import create_url_safe_token

BASE_DIR = Path(__file__).resolve().parent

from dotenv import load_dotenv

load_dotenv()

MAIL_USERNAME = Config.MAIL_USERNAME

MAIL_PASSWORD = os.getenv('MAIL_PASSWORD')

MAIL_FROM = Config.MAIL_FROM

config = ConnectionConfig(
    MAIL_USERNAME = MAIL_USERNAME,
    MAIL_PASSWORD =MAIL_PASSWORD,
    MAIL_FROM =  MAIL_FROM,
    MAIL_PORT = 465,
    MAIL_SERVER = "smtp.gmail.com",
    MAIL_STARTTLS = False,
    MAIL_SSL_TLS = True,
    TEMPLATE_FOLDER = Path(BASE_DIR, 'templates'),
    USE_CREDENTIALS=True,
    VALIDATE_CERTS= True
)


mail = FastMail(
    config
)

def create_message(recipients : List[str], subject : str, body : str):
    
    message = MessageSchema(
        subject=subject,
        recipients= recipients, #List of recipients mail
        body= body,
        subtype= MessageType.html
    )
    return message

async def send_verification_email(recipients, user):
    token = create_url_safe_token({"email": user.email})
    link = f"{Config.SSL_PREFIX}://{Config.FRONTEND_URL}/student/verify/{token}"
    html_message  = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tuitiion Verification</title>
        </head>
        <body>
            <div>
                <h3>Account verification</h3><br>

                <p>Welcome to Tuition, Click on the button below to verify your Account</p>
                <a href="{link}", style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem;text-decoration: none; background: #27B55B; color: white;">Verify your email</a>

                <p>Kindly ignore the email if you did not sign up for Tuition. Thank you!</p>
            </div>
        </body>
        </html>

    """

    message = create_message(
        subject="Email Account verification",
        recipients=recipients,
        body=html_message
    )
    try:
        await mail.send_message(message)
        # return {"message": "Verification email sent successfully"}
    except ChildProcessError as e:
        logging.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")
    



async def send_verification_email_institution(recipients, user):
    token = create_url_safe_token({"email": user.email})
    link = f"{Config.SSL_PREFIX}://{Config.INSTITUTION_URL}/institution/verify/{token}"
    html_message  = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tuitiion Verification</title>
        </head>
        <body>
            <div>
                <h3>Account verification</h3><br>

                <p>Welcome to Tuition, Click on the button below to verify your Account</p>
                <a href="{link}", style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem;text-decoration: none; background: #27B55B; color: white;">Verify your email</a>

                <p>Kindly ignore the email if you did not sign up for Tuition. Thank you!</p>
            </div>
        </body>
        </html>

    """

    message = create_message(
        subject="Email Account verification",
        recipients=recipients,
        body=html_message
    )
    try:
        await mail.send_message(message)
        # return {"message": "Verification email sent successfully"}
    except ChildProcessError as e:
        logging.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")
    

async def send_password_reset_email(recipients, user):
    token = create_url_safe_token({"email": user.email})
    link = f"{Config.SSL_PREFIX}://{Config.DOMAIN}/student/password-reset-confirm/{token}"
    html_message  = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>Tuition Password Modification</title>
        </head>
        <body>
            <div>
                <h3>Reset your Password</h3><br>

                <p>Click the button below to reset your password</p>
                <a href="{link}", style="margin-top: 1rem; padding: 1rem; border-radius: 0.5rem; font-size: 1rem;text-decoration: none; background: #27B55B; color: white;">Reset Password</a>
                <p>Kindly ignore the email if you did not request to change Password, And contact Support</p>
            </div>
        </body>
        </html>

    """
    message = create_message(
        subject="Password Reset Request",
        recipients=recipients,
        body=html_message
    )
    try:
        await mail.send_message(message)
    except ChildProcessError as e:
        logging.error(f"Failed to send email: {e}")
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")



 
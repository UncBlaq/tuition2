import os
import logging

from fastapi import HTTPException, status
# from fastapi.templating import Jinja2Templates
from fastapi_mail import ConnectionConfig, FastMail, MessageSchema

from pathlib import Path
from tuition.config import Config
from tuition.security.jwt import create_url_safe_token

logger = logging.getLogger(__name__)

from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

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
# templates = Jinja2Templates(directory="tuition.templates")


class SmtpMailService:

    def __init__(self, recipient: str | list[str], mail = FastMail(config)):
        
        self.recipient = recipient
        self.mail = mail

    def create_token(self, email: str):
        logger.info("Creating token")
        return create_url_safe_token({"email": email})

    async def send_email(self, subject: str, body : str):
        logger.info("Sending email to %s", self.recipient)
        message = MessageSchema(
            subject=subject,
            recipients=[self.recipient] if isinstance(self.recipient, str) else self.recipient,
            body=body,
            subtype="html"
        )
        try:
            await self.mail.send_message(message)
        except Exception as e:
            logging.error(f"Failed to send email: {e}")
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Failed to send email")

    async def send_verification_email(self, user, route : str = "verify"):
        logger.info("Sending verification email")
        token = self.create_token(self.recipient)
        logger.info("created token: %s", token)
        link = f"{Config.SSL_PREFIX}://{Config.FRONTEND_URL}/{user}/{route}/{token}"
        body = f"""
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
        await self.send_email("Email Account Verification", body)

    async def send_password_reset_email(self, user, route : str = "password-reset-confirm"):
        logger.info("Sending password reset email")
        token = self.create_token(self.recipient)
        logger.info("created token: %s", token)
        link = f"{Config.SSL_PREFIX}://{Config.FRONTEND_URL}/{user}/{route}/{token}"
        body = f"""
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
        await self.send_email("Password Reset Request", body)

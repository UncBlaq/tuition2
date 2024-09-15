from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    SECRET_KEY : str
    ALGORITHM : str
    MAIL_USERNAME : str
    MAIL_PASSWORD : str
    MAIL_FROM : str
    DOMAIN : str
    FRONTEND_URL : str
    SSL_PREFIX : str
    SUPABASE_URL : str
    SUPABASE_KEY : str



    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

Config = Settings()
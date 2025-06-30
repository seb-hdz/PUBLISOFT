from pydantic_settings import BaseSettings, SettingsConfigDict
from supabase import create_client

class Settings(BaseSettings):
    DATABASE_USER: str|None = None
    DATABASE_PWD: str|None = None
    DATABASE_HOST: str|None = None
    DATABASE_PORT: str|None = None
    DATABASE_NAME: str|None = None
    JWT_SECRET: str|None = None

    model_config = SettingsConfigDict(env_file=".env", extra="ignore")
    
settings = Settings()
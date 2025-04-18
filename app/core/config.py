import os
import secrets
from dotenv import load_dotenv
from pydantic_settings import BaseSettings

# Load environment variables
load_dotenv()

class Settings(BaseSettings):
    # App general settings
    APP_NAME: str = os.getenv("APP_NAME", "ECDSA Signature Service")
    APP_ENV: str = os.getenv("APP_ENV", "development")
    APP_PORT: int = int(os.getenv("APP_PORT", "8000"))
    APP_HOST: str = os.getenv("APP_HOST", "0.0.0.0")
    
    # Security
    SECRET_KEY: str = os.getenv("SECRET_KEY", secrets.token_hex(32))
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DB_USER: str = os.getenv("DB_USER", "postgres")
    DB_PASSWORD: str = os.getenv("DB_PASSWORD", "postgres")
    DB_NAME: str = os.getenv("DB_NAME", "ecdsa_signatures")
    DB_HOST: str = os.getenv("DB_HOST", "localhost")
    DB_PORT: str = os.getenv("DB_PORT", "5432")
    DATABASE_URL: str = f"postgresql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # ECDSA Configuration
    # Supported curves: secp256k1, secp384r1, secp521r1
    CURVE_NAME: str = os.getenv("CURVE_NAME", "secp521r1")
    
    class Config:
        env_file = ".env"

settings = Settings() 
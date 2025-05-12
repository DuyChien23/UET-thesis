"""
Settings module for application configuration.
Uses environment variables with fallback to default values.
"""

import os
from functools import lru_cache
from pydantic import BaseSettings, PostgresDsn, validator, Field


class Settings(BaseSettings):
    """
    Application settings, loaded from environment variables.
    Provides fallback default values for local development.
    """
    
    # Application settings
    app_name: str = "Digital Signature Verification API"
    debug: bool = Field(False, env="DEBUG")
    host: str = Field("0.0.0.0", env="HOST")
    port: int = Field(8000, env="PORT")
    
    # Database settings
    postgres_user: str = Field("postgres", env="POSTGRES_USER")
    postgres_password: str = Field("postgres", env="POSTGRES_PASSWORD")
    postgres_host: str = Field("localhost", env="POSTGRES_HOST")
    postgres_port: int = Field(5432, env="POSTGRES_PORT")
    postgres_db: str = Field("digital_signature_db", env="POSTGRES_DB")
    database_url: str = ""
    
    # Redis settings
    redis_host: str = Field("localhost", env="REDIS_HOST")
    redis_port: int = Field(6379, env="REDIS_PORT")
    redis_db: int = Field(0, env="REDIS_DB")
    redis_password: str = Field("", env="REDIS_PASSWORD")
    redis_url: str = ""
    
    # JWT settings
    jwt_secret_key: str = Field("supersecretkey", env="JWT_SECRET_KEY")
    jwt_algorithm: str = Field("HS256", env="JWT_ALGORITHM")
    jwt_expire_minutes: int = Field(60 * 24, env="JWT_EXPIRE_MINUTES")  # 24 hours by default
    
    # CORS settings
    cors_origins: list[str] = Field(["*"], env="CORS_ORIGINS")
    
    @validator("database_url", pre=True)
    def assemble_db_url(cls, v, values):
        """
        Assemble database URL from components if not provided directly.
        """
        if v:
            return v
        
        user = values.get("postgres_user")
        password = values.get("postgres_password")
        host = values.get("postgres_host")
        port = values.get("postgres_port")
        db = values.get("postgres_db")
        
        return f"postgresql+asyncpg://{user}:{password}@{host}:{port}/{db}"
    
    @validator("redis_url", pre=True)
    def assemble_redis_url(cls, v, values):
        """
        Assemble Redis URL from components if not provided directly.
        """
        if v:
            return v
        
        host = values.get("redis_host")
        port = values.get("redis_port")
        db = values.get("redis_db")
        password = values.get("redis_password")
        
        if password:
            return f"redis://:{password}@{host}:{port}/{db}"
        
        return f"redis://{host}:{port}/{db}"
    
    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    """
    Get the application settings, cached for performance.
    
    Returns:
        Settings: The application settings
    """
    return Settings() 
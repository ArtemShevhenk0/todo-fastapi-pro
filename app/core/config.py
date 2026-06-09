from pydantic_settings import BaseSettings, SettingsConfigDict
from pydantic import Field


class Settings(BaseSettings):
    DATABASE_URL: str
    SECRET_KEY: str
    ALGORITHM: str = Field(default="HS256")
    OPENROUTER_API_KEY: str
    UPLOAD_DIR: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int = Field(default=30)
    model_config = SettingsConfigDict(
        env_file='.env',
        env_file_encoding='utf-8',
        extra ='forbid',
        str_strip_whitespace=True
    )
settings = Settings()

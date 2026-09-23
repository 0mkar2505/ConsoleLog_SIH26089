"""
Application configuration management for Console Log Backend.
"""
from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "ConsoleLog"
    APP_ENV: str = "development"
    MONGODB_URI: str = "mongodb+srv://SudoOZU5:password%4088@clusterq.qpjupcx.mongodb.net/sevasetu_dv?retryWrites=true&w=majority"
    MONGODB_DATABASE: str = "sevasetu_dv"
    SECRET_KEY: str = "development-secret-key-change-in-production"
    ALGORITHM: str = "HS256"

    class Config:
        env_file = ".env"
        extra = "ignore"


settings = Settings()

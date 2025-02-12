from dotenv import load_dotenv
from pydantic_settings import BaseSettings
load_dotenv()

class Settings(BaseSettings):
    PGSQL_DATABASE_URL: str
    REDIS_HOST: str
    REDIS_PASSWORD: str
    SECRET_KEY: str
    
    class Config:
        env_file = ".env"
    
settings = Settings()
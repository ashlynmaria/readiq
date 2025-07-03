from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql+asyncpg://readiq:readiq@localhost:5432/readiq"
    JWT_SECRET: str = "changeme"     # fallback for Alembic
    EMAIL_FROM: str = "changeme@example.com"  # fallback for Alembic

    model_config = {
        "env_file": ".env",
        "extra": "ignore"
    }

settings = Settings()

import os

class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql://messaging_user:messaging_password@localhost:5432/messaging_service"
    )

settings = Settings()

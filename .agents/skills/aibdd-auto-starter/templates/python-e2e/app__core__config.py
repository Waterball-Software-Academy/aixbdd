import os


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:postgres@localhost:5432/${DB_NAME}",
    )
    API_PREFIX: str = "/api"


settings = Settings()

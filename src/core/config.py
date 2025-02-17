from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    ENV: str = "development"
    DATABASE_URL: str = "sqlite:///./test.db"
    SECRET_KEY: str = "your-secret-key"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60
    SMTP_USER: str
    SMTP_PASSWORD: str
    SMTP_PORT: int
    EMAILS_FROM_EMAIL: str
    SMTP_HOST: str
    SMTP_TLS: bool

    class Config:
        env_file = ".env"


settings = Settings()

from fastapi_mail import ConnectionConfig
from src.core.config import settings


# SMTP Configuration
conf = ConnectionConfig(
    MAIL_USERNAME=settings.SMTP_USER,
    MAIL_PASSWORD=settings.SMTP_PASSWORD,
    MAIL_PORT=settings.SMTP_PORT,
    MAIL_FROM=settings.EMAILS_FROM_EMAIL,
    MAIL_SERVER=settings.SMTP_HOST,
    MAIL_STARTTLS=settings.SMTP_TLS,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
)

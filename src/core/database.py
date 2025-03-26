from sqlmodel import create_engine, Session
from src.core.config import settings
from sqlalchemy.exc import OperationalError
import psycopg2

DATABASE_URL = settings.DATABASE_URL

engine = create_engine(DATABASE_URL)

try:
    engine.connect()
    print("✅ Database exists!")
except OperationalError:
    print("⚠️ Database does not exist. Creating it now...")

    # Connect to PostgreSQL default database
    conn = psycopg2.connect(
        "dbname=postgres user=postgres password=password host=localhost"
    )
    conn.autocommit = True
    cur = conn.cursor()

    # Create the missing database
    cur.execute("CREATE DATABASE curasphere;")
    cur.close()
    conn.close()

    print("✅ Database 'curasphere' created successfully!")

    # Reconnect after creation
    engine = create_engine(DATABASE_URL)


def get_session():
    with Session(engine) as session:
        yield session

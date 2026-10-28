import os

from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

USER = os.getenv("POSTGRES_USER", "postgres")
PASSWORD = os.getenv("POSTGRES_PASSWORD", "postgres_password")
DB = os.getenv("POSTGRES_DB", "backend_db")
PORT = os.getenv("POSTGRES_PORT", "5433")
HOST = os.getenv("POSTGRES_HOST", "localhost")

DATABASE_URL = f"postgresql+psycopg://{USER}:{PASSWORD}@{HOST}:{PORT}/{DB}"

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

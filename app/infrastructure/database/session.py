from app.core.config import Settings
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

settings = Settings()
engine = create_engine(settings.database_url, echo=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

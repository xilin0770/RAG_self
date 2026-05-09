from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.core.config import settings

engine = create_engine(settings.database_url, echo=False)
SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)


class Base(DeclarativeBase):
    pass


def init_db():
    from app.models import course, document, question, import_task, conversation  # noqa: F401
    Base.metadata.create_all(bind=engine)
    # Ensure content_type column exists on existing import_tasks tables
    try:
        with engine.connect() as conn:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE import_tasks ADD COLUMN content_type VARCHAR(50) DEFAULT ''"
                )
            )
            conn.commit()
    except Exception:
        pass  # column already exists

    # Ensure citations column exists on existing messages tables
    try:
        with engine.connect() as conn:
            conn.execute(
                __import__("sqlalchemy").text(
                    "ALTER TABLE messages ADD COLUMN citations JSON DEFAULT NULL"
                )
            )
            conn.commit()
    except Exception:
        pass  # column already exists


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

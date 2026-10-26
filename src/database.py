import os
from collections.abc import Generator

from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker


DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./moeda_estudantil.db")
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


class Base(DeclarativeBase):
    pass


def get_db() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def create_tables() -> None:
    Base.metadata.create_all(bind=engine)
    # Keep local databases created by earlier releases usable without
    # requiring a destructive reset (Alembic can later own this migration).
    if "professor" in inspect(engine).get_table_names():
        columns = {column["name"] for column in inspect(engine).get_columns("professor")}
        if "ultimo_credito_semestre" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE professor ADD COLUMN ultimo_credito_semestre VARCHAR(7)")
                )

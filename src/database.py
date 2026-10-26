from collections.abc import Generator

from sqlalchemy import create_engine, event, inspect, text
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from src.settings import settings

DATABASE_URL = settings.database_url
IS_SQLITE = DATABASE_URL.startswith("sqlite")
connect_args = {"check_same_thread": False} if IS_SQLITE else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False, expire_on_commit=False)


if IS_SQLITE:

    @event.listens_for(engine, "connect")
    def _enable_foreign_keys(dbapi_connection, _record) -> None:
        # SQLite ignora chaves estrangeiras por padrão; sem isto os vínculos não são protegidos.
        cursor = dbapi_connection.cursor()
        cursor.execute("PRAGMA foreign_keys=ON")
        cursor.close()


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
    # Mantém bancos locais de versões anteriores utilizáveis sem reset destrutivo.
    if "professor" in inspect(engine).get_table_names():
        columns = {column["name"] for column in inspect(engine).get_columns("professor")}
        if "ultimo_credito_semestre" not in columns:
            with engine.begin() as connection:
                connection.execute(
                    text("ALTER TABLE professor ADD COLUMN ultimo_credito_semestre VARCHAR(7)")
                )

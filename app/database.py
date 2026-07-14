from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import declarative_base, sessionmaker

SQLALCHEMY_DATABASE_URL = "sqlite:///./todos.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def init_db() -> None:
    """Create tables and upgrade older SQLite schemas when needed."""
    from app import models  # noqa: F401
    Base.metadata.create_all(bind=engine)


    inspector = inspect(engine)
    if "todos" in inspector.get_table_names():
        columns = {column["name"] for column in inspector.get_columns("todos")}
        if "owner_id" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE todos ADD COLUMN owner_id INTEGER"))
                connection.execute(text("UPDATE todos SET owner_id = 1 WHERE owner_id IS NULL"))
        if "folder_id" not in columns:
            with engine.begin() as connection:
                connection.execute(text("ALTER TABLE todos ADD COLUMN folder_id INTEGER"))



init_db()

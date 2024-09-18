from sqlalchemy.ext.asyncio import create_async_engine

from backend.app.config import DATABASE_HOST, DATABASE_NAME, DATABASE_USER, DATABASE_PASSWORD, DATABASE_PORT


class ManagerSQLAlchemy:

    engine = create_async_engine(
        f"postgresql+asyncpg://{DATABASE_USER}:{DATABASE_PASSWORD}@{DATABASE_HOST}:{DATABASE_PORT}/{DATABASE_NAME}"
    )

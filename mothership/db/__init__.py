from sqlalchemy.ext.asyncio import AsyncEngine, create_async_engine


def new_engine() -> AsyncEngine:
    return create_async_engine(
        "postgresql+asyncpg://postgres:postgres@localhost:5432/mothership"
    )

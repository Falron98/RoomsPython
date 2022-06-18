from contextlib import asynccontextmanager

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

from commands.db import db_path

Base = declarative_base()
global engine

engine = create_async_engine(
    "sqlite+aiosqlite:////{}".format(db_path[3:]),
    connect_args={"check_same_thread": False},
    echo=True,
    future=True
)


@asynccontextmanager
async def get_database() -> AsyncSession:
    global engine

    if engine is None:
        engine = create_async_engine(
            "sqlite+aiosqlite:////{}".format(db_path[3:]),
            connect_args={"check_same_thread": False},
            echo=True,
            future=True
        )
    # async with engine.begin() as conn:
    #     await conn.run_sync(Base.metadata.drop_all)
    #     await conn.run_sync(Base.metadata.create_all)

    async with sessionmaker(
            engine, expire_on_commit=False, class_=AsyncSession
    )() as session:
        yield session

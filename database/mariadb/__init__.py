import os

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import text


engine = create_async_engine(os.getenv("MARIADB_URL"), echo=True)
async_session = sessionmaker(bind=engine, class_=AsyncSession, expire_on_commit=False)
Base = declarative_base()


async def create_tables():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def check_mariadb_connection():
    import time

    start_time = time.time()
    try:
        async with async_session() as session:
            result = await session.execute(text("SELECT 1"))
            result.scalars().one()
            end_time = time.time()
        return {"healthy": True, "ping": round((end_time - start_time), 3)}
    except Exception as e:
        print(f"Database connection error: {e}")
        return {"healthy": False}

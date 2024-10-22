import os
from typing import Annotated
from fastapi import Depends
from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("No DATABASE_URL set for SQLAlchemy engine")

engine = create_async_engine(DATABASE_URL, echo=False)

SessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,  # Use AsyncSession
    autocommit=False,
    autoflush=False,
)

Base = declarative_base()

# Dependency to provide the async session
async def get_db():
    async with SessionLocal() as db:
        try:
            yield db
        finally:
            await db.close()

# Annotated to declare dependency for FastAPI routes
db_dependency = Annotated[AsyncSession, Depends(get_db)]


import os

from dotenv import load_dotenv
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

load_dotenv()

db_password = os.getenv("DB_PASSWORD")
db_user = os.getenv("DB_USER")
db_name = os.getenv("DB_NAME")
DATABASE_URL = f"postgresql+asyncpg://{db_user}:{db_password}@localhost/{db_name}"



engine = create_async_engine(DATABASE_URL, echo=True)
SessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()

async def get_db():
    async with SessionLocal() as session:
        yield session



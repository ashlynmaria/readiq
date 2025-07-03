from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from core.config import settings

# create Base
Base = declarative_base()

# create async engine
engine = create_async_engine(settings.DATABASE_URL, echo=True)

# session factory
async_session = sessionmaker(
    engine, class_=AsyncSession, expire_on_commit=False
)

# dependency to get DB session
async def get_db():
    async with async_session() as session:
        yield session

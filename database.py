from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import sessionmaker

DATABASE_URL = (
    "postgresql+asyncpg://postgres:123@localhost:5432/testdb"
)

engine = create_async_engine(
    DATABASE_URL,
    echo=False,

    pool_size=20,
    max_overflow=10,

    pool_timeout=30,
    pool_recycle=1800
)

AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False
)
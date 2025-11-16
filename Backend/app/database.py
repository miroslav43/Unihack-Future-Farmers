from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from app.config import settings
import ssl

# Parse and clean the database URL for asyncpg
# asyncpg doesn't support sslmode parameter in URL, we need to pass it as connect_args
database_url = settings.NEON_DB
# Remove sslmode and channel_binding from URL as asyncpg handles SSL differently
if "?" in database_url:
    base_url = database_url.split("?")[0]
    database_url = base_url

# Convert postgresql:// to postgresql+asyncpg://
DATABASE_URL = database_url.replace("postgresql://", "postgresql+asyncpg://")

# Create SSL context for Neon DB (requires SSL)
ssl_context = ssl.create_default_context()
ssl_context.check_hostname = False
ssl_context.verify_mode = ssl.CERT_NONE

# Create async engine with SSL
engine = create_async_engine(
    DATABASE_URL,
    echo=True,
    future=True,
    connect_args={
        "ssl": ssl_context,
        "prepared_statement_cache_size": 0,  # avoid InvalidCachedStatement after schema changes
    }
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False
)

# Create base class for models
Base = declarative_base()


async def get_db():
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        finally:
            await session.close()


async def init_db():
    """Initialize database - create tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    print("✅ Database tables created")


async def close_db():
    """Close database connections"""
    await engine.dispose()
    print("✅ Database connections closed")

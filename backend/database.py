"""
Database configuration and models for SwellSense
Uses async SQLAlchemy with PostgreSQL (Neon)
"""
from sqlalchemy import Column, Integer, Float, DateTime, String
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base
from datetime import datetime
import os
from typing import AsyncGenerator

# Database URL from environment
DATABASE_URL = os.getenv("DATABASE_URL", "")

# Convert postgresql:// to postgresql+asyncpg:// and remove incompatible params
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://")
    # Remove sslmode and channel_binding params that asyncpg doesn't support in URL
    # asyncpg handles SSL automatically with Neon
    DATABASE_URL = DATABASE_URL.split("?")[0] + "?ssl=require" if "?" in DATABASE_URL else DATABASE_URL

# Create async engine
engine = create_async_engine(
    DATABASE_URL,
    echo=False,  # Set to True for SQL query logging during development
    future=True,
    pool_pre_ping=True,  # Verify connections before using
)

# Create async session factory
AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autocommit=False,
    autoflush=False,
)

# Base class for models
Base = declarative_base()


class SurfCondition(Base):
    """Model for surf conditions data from NOAA buoys"""
    __tablename__ = "surf_conditions"

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, nullable=False, index=True, default=datetime.utcnow)
    wave_height = Column(Float, nullable=True)  # meters
    wave_period = Column(Float, nullable=True)  # seconds
    wind_speed = Column(Float, nullable=True)   # m/s
    tide_level = Column(Float, nullable=True)   # meters (optional for now)
    buoy_id = Column(String(10), nullable=True, index=True)  # NOAA buoy station ID
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "wave_height": self.wave_height,
            "wave_period": self.wave_period,
            "wind_speed": self.wind_speed,
            "tide_level": self.tide_level,
            "buoy_id": self.buoy_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency for getting async database sessions"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()


async def init_db():
    """Initialize database tables"""
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

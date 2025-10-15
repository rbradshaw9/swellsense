"""
Database configuration and models for SwellSense
Uses async SQLAlchemy with PostgreSQL (Neon)
"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Index
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


class BuoyStation(Base):
    """Model for NOAA buoy station metadata and locations"""
    __tablename__ = "buoy_stations"

    id = Column(Integer, primary_key=True, index=True)
    station_id = Column(String(10), unique=True, nullable=False, index=True)
    name = Column(String(200), nullable=False)
    region = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        """Convert model to dictionary"""
        return {
            "id": self.id,
            "station_id": self.station_id,
            "name": self.name,
            "region": self.region,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }
    
    def distance_to(self, lat: float, lon: float) -> float:
        """
        Calculate distance in miles from this buoy to given coordinates
        Uses Haversine formula
        """
        import math
        
        # Earth radius in miles
        R = 3959
        
        lat1_rad = math.radians(self.latitude)
        lat2_rad = math.radians(lat)
        delta_lat = math.radians(lat - self.latitude)
        delta_lon = math.radians(lon - self.longitude)
        
        a = (math.sin(delta_lat / 2) ** 2 +
             math.cos(lat1_rad) * math.cos(lat2_rad) *
             math.sin(delta_lon / 2) ** 2)
        c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
        
        return R * c


class MarineCondition(Base):
    """Global marine conditions from StormGlass, Met.no, etc."""
    __tablename__ = "marine_conditions"
    __table_args__ = (
        Index('idx_marine_location_time', 'latitude', 'longitude', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, index=True)  # 'stormglass', 'metno', 'noaa'
    buoy_id = Column(String(10), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    wave_height = Column(Float, nullable=True)  # meters
    swell_period = Column(Float, nullable=True)  # seconds
    wave_direction = Column(Float, nullable=True)  # degrees
    water_temperature = Column(Float, nullable=True)  # celsius
    current_speed = Column(Float, nullable=True)  # m/s
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "buoy_id": self.buoy_id,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "wave_height": self.wave_height,
            "swell_period": self.swell_period,
            "wave_direction": self.wave_direction,
            "water_temperature": self.water_temperature,
            "current_speed": self.current_speed,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class WeatherData(Base):
    """Weather data from OpenWeatherMap"""
    __tablename__ = "weather_data"
    __table_args__ = (
        Index('idx_weather_location_time', 'latitude', 'longitude', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, default='openweather')
    buoy_id = Column(String(10), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    wind_speed = Column(Float, nullable=True)  # m/s
    wind_gust = Column(Float, nullable=True)  # m/s
    wind_direction = Column(Float, nullable=True)  # degrees
    temperature = Column(Float, nullable=True)  # celsius
    pressure = Column(Float, nullable=True)  # hPa
    visibility = Column(Float, nullable=True)  # meters
    description = Column(String(200), nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "wind_speed": self.wind_speed,
            "wind_gust": self.wind_gust,
            "wind_direction": self.wind_direction,
            "temperature": self.temperature,
            "pressure": self.pressure,
            "visibility": self.visibility,
            "description": self.description,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class TideData(Base):
    """Tide data from WorldTides API"""
    __tablename__ = "tides"
    __table_args__ = (
        Index('idx_tide_location_time', 'latitude', 'longitude', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, default='worldtides')
    buoy_id = Column(String(10), nullable=True, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    tide_height_meters = Column(Float, nullable=False)
    tide_type = Column(String(10), nullable=True)  # 'high', 'low', or None for height
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "tide_height_meters": self.tide_height_meters,
            "tide_type": self.tide_type,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class OceanCurrent(Base):
    """Ocean current data from Copernicus/Mercator"""
    __tablename__ = "ocean_currents"
    __table_args__ = (
        Index('idx_current_location_time', 'latitude', 'longitude', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    source = Column(String(50), nullable=False, default='copernicus')
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    current_u = Column(Float, nullable=True)  # eastward current m/s
    current_v = Column(Float, nullable=True)  # northward current m/s
    sea_surface_temp = Column(Float, nullable=True)  # celsius
    sea_surface_height = Column(Float, nullable=True)  # meters
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "source": self.source,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "current_u": self.current_u,
            "current_v": self.current_v,
            "sea_surface_temp": self.sea_surface_temp,
            "sea_surface_height": self.sea_surface_height,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class DriftingBuoy(Base):
    """Drifting buoy data from Sofar Spotter"""
    __tablename__ = "drifting_buoys"
    __table_args__ = (
        Index('idx_drifting_location_time', 'latitude', 'longitude', 'timestamp'),
    )

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, index=True)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    timestamp = Column(DateTime, nullable=False, index=True)
    wave_height = Column(Float, nullable=True)  # meters
    wave_period = Column(Float, nullable=True)  # seconds
    wind_speed = Column(Float, nullable=True)  # m/s
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "timestamp": self.timestamp.isoformat() if self.timestamp else None,
            "wave_height": self.wave_height,
            "wave_period": self.wave_period,
            "wind_speed": self.wind_speed,
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

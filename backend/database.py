"""
Database configuration and models for SwellSense
Uses async SQLAlchemy with PostgreSQL (Neon)
"""
from sqlalchemy import Column, Integer, Float, DateTime, String, Index, Boolean, JSON, Text, ForeignKey
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import declarative_base, relationship
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


class AlertPreference(Base):
    """User alert preferences for personalized surf notifications"""
    __tablename__ = "alert_preferences"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), unique=True, nullable=False, index=True)  # Supabase user ID
    
    # Timing preferences
    daily_brief_enabled = Column(Boolean, default=True)
    daily_brief_time = Column(String(5), default="06:00")  # HH:MM format in user's timezone
    timezone = Column(String(50), default="America/Puerto_Rico")
    
    # Alert types
    breaking_news_enabled = Column(Boolean, default=True)  # Real-time "it's firing!" alerts
    upcoming_swells_enabled = Column(Boolean, default=True)  # "Big swell arriving Thursday"
    
    # Location-based alerts
    alert_for_favorites = Column(Boolean, default=True)  # Monitor saved favorite spots
    alert_for_current_location = Column(Boolean, default=False)  # "You're near Blacks Beach and it's good!"
    alert_radius_miles = Column(Integer, default=25)  # How far from current location to check
    
    # Quality thresholds (1-10 scale)
    minimum_quality_score = Column(Integer, default=7)  # Only alert if spot scores 7+ out of 10
    only_alert_when_better = Column(Boolean, default=False)  # Only alert if better than last session
    
    # Push notification token
    push_token = Column(String(255), nullable=True)  # Expo push notification token
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "daily_brief_enabled": self.daily_brief_enabled,
            "daily_brief_time": self.daily_brief_time,
            "timezone": self.timezone,
            "breaking_news_enabled": self.breaking_news_enabled,
            "upcoming_swells_enabled": self.upcoming_swells_enabled,
            "alert_for_favorites": self.alert_for_favorites,
            "alert_for_current_location": self.alert_for_current_location,
            "alert_radius_miles": self.alert_radius_miles,
            "minimum_quality_score": self.minimum_quality_score,
            "only_alert_when_better": self.only_alert_when_better,
            "push_token": self.push_token,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None,
        }


class FavoriteSpot(Base):
    """User's favorite surf spots for personalized alerts"""
    __tablename__ = "favorite_spots"
    __table_args__ = (
        Index('idx_user_spots', 'user_id', 'spot_name'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)  # Supabase user ID
    
    # Spot details
    spot_name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    region = Column(String(100), nullable=True)  # "Puerto Rico", "California", etc.
    
    # User notes
    notes = Column(Text, nullable=True)  # "Best at high tide", "Watch out for rocks"
    
    # Priority (for daily brief ranking)
    priority = Column(Integer, default=1)  # 1 = highest priority, 10 = lowest
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "spot_name": self.spot_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "region": self.region,
            "notes": self.notes,
            "priority": self.priority,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class AlertHistory(Base):
    """Track sent alerts to avoid duplicates and measure engagement"""
    __tablename__ = "alert_history"
    __table_args__ = (
        Index('idx_user_alert_time', 'user_id', 'sent_at'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Alert details
    alert_type = Column(String(50), nullable=False)  # "daily_brief", "breaking_news", "upcoming_swell"
    spot_name = Column(String(200), nullable=False)
    title = Column(String(200), nullable=False)
    message = Column(Text, nullable=False)
    
    # Conditions at time of alert
    conditions_snapshot = Column(JSON, nullable=True)  # {"wave_height": 4, "period": 12, "wind": "offshore"}
    quality_score = Column(Integer, nullable=True)  # 1-10 score
    
    # Engagement tracking
    sent_at = Column(DateTime, nullable=False, default=datetime.utcnow, index=True)
    opened_at = Column(DateTime, nullable=True)  # When user tapped notification
    session_logged = Column(Boolean, default=False)  # Did user surf this spot after alert?
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "alert_type": self.alert_type,
            "spot_name": self.spot_name,
            "title": self.title,
            "message": self.message,
            "conditions_snapshot": self.conditions_snapshot,
            "quality_score": self.quality_score,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "opened_at": self.opened_at.isoformat() if self.opened_at else None,
            "session_logged": self.session_logged,
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class SurfSession(Base):
    """User surf sessions (manual logging or imported from HealthKit/Dawn Patrol)"""
    __tablename__ = "surf_sessions"
    __table_args__ = (
        Index('idx_user_session_time', 'user_id', 'session_date'),
    )

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String(100), nullable=False, index=True)
    
    # Session basics
    spot_name = Column(String(200), nullable=False)
    latitude = Column(Float, nullable=True)
    longitude = Column(Float, nullable=True)
    session_date = Column(DateTime, nullable=False, index=True)
    duration_minutes = Column(Integer, nullable=True)
    
    # Session details
    waves_caught = Column(Integer, nullable=True)
    rating = Column(Integer, nullable=True)  # User rating 1-10
    board_type = Column(String(50), nullable=True)  # "shortboard", "longboard", etc.
    
    # Conditions at time of session
    wave_height_ft = Column(Float, nullable=True)
    swell_period_sec = Column(Float, nullable=True)
    wind_speed_mph = Column(Float, nullable=True)
    wind_direction = Column(String(20), nullable=True)
    tide = Column(String(20), nullable=True)  # "low", "mid", "high"
    crowd_level = Column(String(20), nullable=True)  # "empty", "light", "moderate", "packed"
    
    # User notes
    notes = Column(Text, nullable=True)
    
    # Photos
    photo_urls = Column(JSON, nullable=True)  # Array of photo URLs
    
    # Import source
    import_source = Column(String(50), default="manual")  # "manual", "healthkit", "dawn_patrol", "waves"
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "spot_name": self.spot_name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "session_date": self.session_date.isoformat() if self.session_date else None,
            "duration_minutes": self.duration_minutes,
            "waves_caught": self.waves_caught,
            "rating": self.rating,
            "board_type": self.board_type,
            "wave_height_ft": self.wave_height_ft,
            "swell_period_sec": self.swell_period_sec,
            "wind_speed_mph": self.wind_speed_mph,
            "wind_direction": self.wind_direction,
            "tide": self.tide,
            "crowd_level": self.crowd_level,
            "notes": self.notes,
            "photo_urls": self.photo_urls,
            "import_source": self.import_source,
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

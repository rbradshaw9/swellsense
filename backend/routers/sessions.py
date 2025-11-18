"""
Sessions Router - Manual session entry and history tracking
Enables AI to learn user preferences from actual surf sessions
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel, Field
from typing import Optional, List
from datetime import datetime

from database import get_db, SurfSession
from auth import verify_token, AuthUser

router = APIRouter()


class SessionCreate(BaseModel):
    """Create new surf session"""
    spot_name: str = Field(..., min_length=1, max_length=200, description="Name of surf spot")
    latitude: Optional[float] = Field(None, ge=-90, le=90, description="Spot latitude")
    longitude: Optional[float] = Field(None, ge=-180, le=180, description="Spot longitude")
    session_date: datetime = Field(..., description="Date/time of session (ISO 8601)")
    duration_minutes: Optional[int] = Field(None, ge=1, le=720, description="Session length in minutes")
    waves_caught: Optional[int] = Field(None, ge=0, le=500, description="Number of waves caught")
    rating: Optional[int] = Field(None, ge=1, le=10, description="How was the session? 1-10")
    board_type: Optional[str] = Field(None, description="shortboard, longboard, funboard, fish, gun")
    wave_height_ft: Optional[float] = Field(None, ge=0, le=50, description="Wave height in feet")
    swell_period_sec: Optional[float] = Field(None, ge=0, le=30, description="Swell period in seconds")
    wind_speed_mph: Optional[float] = Field(None, ge=0, le=100, description="Wind speed in mph")
    wind_direction: Optional[str] = Field(None, description="N, NE, E, SE, S, SW, W, NW, offshore, onshore")
    tide: Optional[str] = Field(None, description="low, mid, high, rising, falling")
    crowd_level: Optional[str] = Field(None, description="empty, light, moderate, packed")
    notes: Optional[str] = Field(None, max_length=2000, description="Session notes/highlights")
    photo_urls: Optional[List[str]] = Field(None, description="URLs of session photos")

    class Config:
        json_schema_extra = {
            "example": {
                "spot_name": "Tres Palmas",
                "latitude": 18.4663,
                "longitude": -67.0371,
                "session_date": "2024-11-18T07:30:00Z",
                "duration_minutes": 90,
                "waves_caught": 12,
                "rating": 9,
                "board_type": "shortboard",
                "wave_height_ft": 4.5,
                "swell_period_sec": 12.0,
                "wind_speed_mph": 8.0,
                "wind_direction": "offshore",
                "tide": "high",
                "crowd_level": "light",
                "notes": "Super fun morning! Clean waves, light crowd. Caught some great lefts."
            }
        }


class SessionUpdate(BaseModel):
    """Update existing session"""
    spot_name: Optional[str] = Field(None, min_length=1, max_length=200)
    latitude: Optional[float] = Field(None, ge=-90, le=90)
    longitude: Optional[float] = Field(None, ge=-180, le=180)
    session_date: Optional[datetime] = None
    duration_minutes: Optional[int] = Field(None, ge=1, le=720)
    waves_caught: Optional[int] = Field(None, ge=0, le=500)
    rating: Optional[int] = Field(None, ge=1, le=10)
    board_type: Optional[str] = None
    wave_height_ft: Optional[float] = Field(None, ge=0, le=50)
    swell_period_sec: Optional[float] = Field(None, ge=0, le=30)
    wind_speed_mph: Optional[float] = Field(None, ge=0, le=100)
    wind_direction: Optional[str] = None
    tide: Optional[str] = None
    crowd_level: Optional[str] = None
    notes: Optional[str] = Field(None, max_length=2000)
    photo_urls: Optional[List[str]] = None


class SessionResponse(BaseModel):
    """Session response model"""
    id: int
    user_id: str
    spot_name: str
    latitude: Optional[float]
    longitude: Optional[float]
    session_date: datetime
    duration_minutes: Optional[int]
    waves_caught: Optional[int]
    rating: Optional[int]
    board_type: Optional[str]
    wave_height_ft: Optional[float]
    swell_period_sec: Optional[float]
    wind_speed_mph: Optional[float]
    wind_direction: Optional[str]
    tide: Optional[str]
    crowd_level: Optional[str]
    notes: Optional[str]
    photo_urls: Optional[List[str]]
    import_source: str
    created_at: datetime

    class Config:
        from_attributes = True


class SessionStats(BaseModel):
    """User session statistics"""
    total_sessions: int
    total_waves_caught: int
    total_hours: float
    average_rating: float
    favorite_spot: Optional[str]
    favorite_board: Optional[str]
    spots_surfed: int
    best_conditions: Optional[dict]


@router.post("/", response_model=SessionResponse, status_code=201)
async def create_session(
    session: SessionCreate,
    current_user: AuthUser = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Log a new surf session manually
    
    This is the foundation for AI learning - the more sessions you log,
    the better SwellSense understands your preferences!
    """
    # Create session record
    db_session = SurfSession(
        user_id=current_user.id,
        spot_name=session.spot_name,
        latitude=session.latitude,
        longitude=session.longitude,
        session_date=session.session_date,
        duration_minutes=session.duration_minutes,
        waves_caught=session.waves_caught,
        rating=session.rating,
        board_type=session.board_type,
        wave_height_ft=session.wave_height_ft,
        swell_period_sec=session.swell_period_sec,
        wind_speed_mph=session.wind_speed_mph,
        wind_direction=session.wind_direction,
        tide=session.tide,
        crowd_level=session.crowd_level,
        notes=session.notes,
        photo_urls=session.photo_urls,
        import_source="manual"
    )
    
    db.add(db_session)
    await db.commit()
    await db.refresh(db_session)
    
    return db_session


@router.get("/", response_model=List[SessionResponse])
async def list_sessions(
    limit: int = Query(50, ge=1, le=200, description="Max sessions to return"),
    offset: int = Query(0, ge=0, description="Number of sessions to skip"),
    spot_name: Optional[str] = Query(None, description="Filter by spot name"),
    min_rating: Optional[int] = Query(None, ge=1, le=10, description="Minimum rating filter"),
    current_user: AuthUser = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's session history
    
    Returns sessions sorted by date (most recent first)
    """
    # Build query
    query = select(SurfSession).where(SurfSession.user_id == current_user.id)
    
    # Apply filters
    if spot_name:
        query = query.where(SurfSession.spot_name.ilike(f"%{spot_name}%"))
    if min_rating:
        query = query.where(SurfSession.rating >= min_rating)
    
    # Order by date descending
    query = query.order_by(desc(SurfSession.session_date))
    
    # Apply pagination
    query = query.offset(offset).limit(limit)
    
    # Execute
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    return sessions


@router.get("/stats", response_model=SessionStats)
async def get_session_stats(
    current_user: AuthUser = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """
    Get user's surf statistics
    
    Provides insights into surfing habits and preferences
    """
    # Get all user sessions
    query = select(SurfSession).where(SurfSession.user_id == current_user.id)
    result = await db.execute(query)
    sessions = result.scalars().all()
    
    if not sessions:
        return SessionStats(
            total_sessions=0,
            total_waves_caught=0,
            total_hours=0.0,
            average_rating=0.0,
            favorite_spot=None,
            favorite_board=None,
            spots_surfed=0,
            best_conditions=None
        )
    
    # Calculate stats
    total_sessions = len(sessions)
    total_waves = sum(s.waves_caught or 0 for s in sessions)
    total_minutes = sum(s.duration_minutes or 0 for s in sessions)
    total_hours = round(total_minutes / 60, 1)
    
    # Average rating (only sessions with ratings)
    rated_sessions = [s for s in sessions if s.rating is not None]
    avg_rating = round(sum(s.rating for s in rated_sessions) / len(rated_sessions), 1) if rated_sessions else 0.0
    
    # Favorite spot (most frequent)
    spot_counts = {}
    for s in sessions:
        spot_counts[s.spot_name] = spot_counts.get(s.spot_name, 0) + 1
    favorite_spot = max(spot_counts, key=spot_counts.get) if spot_counts else None
    
    # Favorite board (most frequent)
    board_counts = {}
    for s in sessions:
        if s.board_type:
            board_counts[s.board_type] = board_counts.get(s.board_type, 0) + 1
    favorite_board = max(board_counts, key=board_counts.get) if board_counts else None
    
    # Unique spots
    spots_surfed = len(set(s.spot_name for s in sessions))
    
    # Best conditions (from highest rated session)
    best_session = max(rated_sessions, key=lambda s: s.rating) if rated_sessions else None
    best_conditions = None
    if best_session and best_session.wave_height_ft:
        best_conditions = {
            "wave_height_ft": best_session.wave_height_ft,
            "swell_period_sec": best_session.swell_period_sec,
            "wind_direction": best_session.wind_direction,
            "tide": best_session.tide,
            "spot": best_session.spot_name,
            "rating": best_session.rating
        }
    
    return SessionStats(
        total_sessions=total_sessions,
        total_waves_caught=total_waves,
        total_hours=total_hours,
        average_rating=avg_rating,
        favorite_spot=favorite_spot,
        favorite_board=favorite_board,
        spots_surfed=spots_surfed,
        best_conditions=best_conditions
    )


@router.get("/{session_id}", response_model=SessionResponse)
async def get_session(
    session_id: int,
    current_user: AuthUser = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Get a specific session by ID"""
    query = select(SurfSession).where(
        SurfSession.id == session_id,
        SurfSession.user_id == current_user.id
    )
    result = await db.execute(query)
    session = result.scalar_one_or_none()
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session


@router.patch("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_update: SessionUpdate,
    current_user: AuthUser = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Update an existing session"""
    # Get session
    query = select(SurfSession).where(
        SurfSession.id == session_id,
        SurfSession.user_id == current_user.id
    )
    result = await db.execute(query)
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    # Update fields
    update_data = session_update.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(db_session, field, value)
    
    await db.commit()
    await db.refresh(db_session)
    
    return db_session


@router.delete("/{session_id}", status_code=204)
async def delete_session(
    session_id: int,
    current_user: AuthUser = Depends(verify_token),
    db: AsyncSession = Depends(get_db)
):
    """Delete a session"""
    # Get session
    query = select(SurfSession).where(
        SurfSession.id == session_id,
        SurfSession.user_id == current_user.id
    )
    result = await db.execute(query)
    db_session = result.scalar_one_or_none()
    
    if not db_session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    await db.delete(db_session)
    await db.commit()
    
    return None

"""
Utility functions for buoy location matching and selection
"""
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional, Tuple
import re

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import BuoyStation


async def get_buoy_by_location(
    db: AsyncSession,
    location: Optional[str] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None
) -> Optional[BuoyStation]:
    """
    Find the best NOAA buoy based on location string or coordinates
    
    Args:
        db: Database session
        location: Location string (e.g., "western PR", "California", "Florida")
        latitude: Latitude coordinate
        longitude: Longitude coordinate
    
    Returns:
        BuoyStation object or None if no match found
    
    Priority:
        1. If lat/lon provided, find nearest buoy
        2. If location string provided, match by region name
        3. Return None if no match
    """
    # Priority 1: Coordinates - find nearest buoy
    if latitude is not None and longitude is not None:
        result = await db.execute(select(BuoyStation))
        all_buoys = result.scalars().all()
        
        if not all_buoys:
            return None
        
        # Calculate distances and find nearest
        nearest_buoy = min(
            all_buoys,
            key=lambda buoy: buoy.distance_to(latitude, longitude)
        )
        
        return nearest_buoy
    
    # Priority 2: Location string - match by region
    if location:
        # Normalize location string
        location_lower = location.lower().strip()
        
        # Try exact region match first
        result = await db.execute(
            select(BuoyStation).where(
                BuoyStation.region.ilike(f"%{location}%")
            )
        )
        buoy = result.scalar_one_or_none()
        
        if buoy:
            return buoy
        
        # Try name match
        result = await db.execute(
            select(BuoyStation).where(
                BuoyStation.name.ilike(f"%{location}%")
            )
        )
        buoy = result.scalar_one_or_none()
        
        if buoy:
            return buoy
        
        # Try common abbreviations and aliases
        location_aliases = {
            "pr": "puerto rico",
            "western pr": "western puerto rico",
            "west pr": "western puerto rico",
            "fl": "florida",
            "ca": "california",
            "socal": "southern california",
            "norcal": "northern california",
            "gulf": "gulf of mexico",
            "hi": "hawaii",
        }
        
        normalized_location = location_aliases.get(location_lower, location_lower)
        
        result = await db.execute(
            select(BuoyStation).where(
                BuoyStation.region.ilike(f"%{normalized_location}%")
            )
        )
        buoy = result.scalar_one_or_none()
        
        return buoy
    
    # No location info provided - return None
    return None


async def get_default_buoy(db: AsyncSession) -> Optional[BuoyStation]:
    """
    Get the default buoy (station 41043 - Florida)
    Falls back to any buoy if default not found
    
    Args:
        db: Database session
    
    Returns:
        BuoyStation object or None
    """
    # Try to get default buoy (41043)
    result = await db.execute(
        select(BuoyStation).where(BuoyStation.station_id == "41043")
    )
    buoy = result.scalar_one_or_none()
    
    if buoy:
        return buoy
    
    # Fallback: return first buoy in database
    result = await db.execute(select(BuoyStation).limit(1))
    return result.scalar_one_or_none()


def parse_coordinates(coord_string: str) -> Optional[Tuple[float, float]]:
    """
    Parse coordinate string into (lat, lon) tuple
    
    Supports formats:
        - "29.2,-79.9"
        - "29.2, -79.9"
        - "(29.2, -79.9)"
    
    Args:
        coord_string: String containing coordinates
    
    Returns:
        (latitude, longitude) tuple or None if invalid
    """
    if not coord_string:
        return None
    
    # Remove parentheses and whitespace
    cleaned = coord_string.replace("(", "").replace(")", "").strip()
    
    # Split by comma
    parts = cleaned.split(",")
    
    if len(parts) != 2:
        return None
    
    try:
        lat = float(parts[0].strip())
        lon = float(parts[1].strip())
        
        # Validate ranges
        if not (-90 <= lat <= 90):
            return None
        if not (-180 <= lon <= 180):
            return None
        
        return (lat, lon)
    except ValueError:
        return None

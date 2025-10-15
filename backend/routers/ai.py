"""
AI Query API endpoints for SwellSense
Intelligent surf recommendations using OpenAI and NOAA data
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, desc
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta
import os
import logging

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from database import get_db, SurfCondition, BuoyStation
from utils.buoy_utils import get_buoy_by_location, get_default_buoy

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai"])


class AIQuery(BaseModel):
    """Request model for AI surf queries"""
    query: str
    location: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    skill_level: Optional[str] = "intermediate"  # beginner, intermediate, advanced


class AIResponse(BaseModel):
    """Response model for AI surf recommendations"""
    query: str
    recommendation: str
    confidence: float
    explanation: str
    data_timestamp: Optional[str] = None
    station_used: Optional[str] = None
    region: Optional[str] = None


async def fetch_recent_surf_data(db: AsyncSession, buoy_id: Optional[str] = None, hours: int = 24) -> dict:
    """
    Fetch recent surf conditions from database for AI context
    
    Args:
        db: Database session
        buoy_id: Optional specific buoy to query
        hours: Number of hours of historical data to fetch
    
    Returns:
        Dictionary with formatted surf data
    """
    try:
        # Build query with optional buoy filter
        latest_query = select(SurfCondition)
        if buoy_id:
            latest_query = latest_query.where(SurfCondition.buoy_id == buoy_id)
        latest_query = latest_query.order_by(desc(SurfCondition.timestamp)).limit(1)
        
        latest_result = await db.execute(latest_query)
        latest = latest_result.scalar_one_or_none()
        
        # Get recent readings for trend analysis
        time_threshold = datetime.utcnow() - timedelta(hours=hours)
        recent_query = select(SurfCondition).where(
            SurfCondition.timestamp >= time_threshold
        )
        if buoy_id:
            recent_query = recent_query.where(SurfCondition.buoy_id == buoy_id)
        recent_query = recent_query.order_by(desc(SurfCondition.timestamp)).limit(10)
        
        recent_result = await db.execute(recent_query)
        recent_conditions = recent_result.scalars().all()
        
        if not latest:
            return {
                "status": "no_data",
                "message": "No surf data available",
                "timestamp": None
            }
        
        # Calculate averages for trends
        wave_heights = [c.wave_height for c in recent_conditions if c.wave_height is not None]
        wind_speeds = [c.wind_speed for c in recent_conditions if c.wind_speed is not None]
        wave_periods = [c.wave_period for c in recent_conditions if c.wave_period is not None]
        
        avg_wave_height = sum(wave_heights) / len(wave_heights) if wave_heights else None
        avg_wind_speed = sum(wind_speeds) / len(wind_speeds) if wind_speeds else None
        avg_wave_period = sum(wave_periods) / len(wave_periods) if wave_periods else None
        
        # Format data for AI context
        context_data = {
            "status": "success",
            "current": {
                "wave_height_m": latest.wave_height,
                "wave_height_ft": round(latest.wave_height * 3.281, 1) if latest.wave_height else None,
                "wave_period_sec": latest.wave_period,
                "wind_speed_ms": latest.wind_speed,
                "wind_speed_mph": round(latest.wind_speed * 2.237, 1) if latest.wind_speed else None,
                "buoy_id": latest.buoy_id,
                "timestamp": latest.timestamp.isoformat()
            },
            "trends_24h": {
                "avg_wave_height_ft": round(avg_wave_height * 3.281, 1) if avg_wave_height else None,
                "avg_wind_speed_mph": round(avg_wind_speed * 2.237, 1) if avg_wind_speed else None,
                "avg_wave_period_sec": round(avg_wave_period, 1) if avg_wave_period else None,
                "readings_count": len(recent_conditions)
            },
            "data_source": f"NOAA Buoy {latest.buoy_id}" if latest.buoy_id else "NOAA Buoy Network"
        }
        
        logger.info(f"Fetched surf data: {context_data}")
        return context_data
        
    except Exception as e:
        logger.error(f"Error fetching surf data: {e}")
        raise HTTPException(status_code=500, detail=f"Database error: {str(e)}")


def build_ai_prompt(query: str, surf_data: dict, skill_level: str) -> str:
    """
    Build the prompt for OpenAI API with surf data context
    
    Args:
        query: User's natural language question
        surf_data: Recent surf conditions from database
        skill_level: User's skill level (beginner, intermediate, advanced)
    
    Returns:
        Formatted prompt string for OpenAI
    """
    if surf_data["status"] == "no_data":
        return f"""You are SurfGPT, an AI surf forecasting assistant for SwellSense.

User Question: {query}

Unfortunately, there is no current surf data available from NOAA buoys at this time.

Please provide a helpful response explaining that surf data is temporarily unavailable and suggest checking back later or visiting the forecast page when data is available.

Respond in JSON format with these fields:
- recommendation: Brief advice (max 100 words)
- confidence: 0.0 (no data available)
- explanation: Why no data is available and what to do next
"""
    
    current = surf_data["current"]
    trends = surf_data["trends_24h"]
    
    return f"""You are SurfGPT, an AI surf forecasting assistant for SwellSense. You provide intelligent, personalized surf recommendations based on real-time NOAA buoy data.

User Question: {query}
User Skill Level: {skill_level}

Current Surf Conditions (from {surf_data["data_source"]}):
- Wave Height: {current["wave_height_ft"]}ft ({current["wave_height_m"]}m)
- Wave Period: {current["wave_period_sec"]} seconds
- Wind Speed: {current["wind_speed_mph"]}mph ({current["wind_speed_ms"]}m/s)
- Data Timestamp: {current["timestamp"]}

24-Hour Trends:
- Average Wave Height: {trends["avg_wave_height_ft"]}ft
- Average Wind Speed: {trends["avg_wind_speed_mph"]}mph
- Average Wave Period: {trends["avg_wave_period_sec"]} seconds
- Total Readings: {trends["readings_count"]}

Instructions:
1. Analyze the surf conditions for a {skill_level} surfer
2. Consider wave height, period (swell quality), and wind conditions
3. Provide actionable recommendations about when/where to surf
4. Rate your confidence (0.0-1.0) based on data quality and conditions
5. Explain your reasoning in simple, friendly terms

Surf Quality Guidelines:
- Wave Period >10s = Good quality swell (powerful, organized)
- Wave Period 7-10s = Fair quality (rideable)
- Wave Period <7s = Poor quality (choppy wind swell)
- Wind Speed <10mph = Clean conditions
- Wind Speed >15mph = Choppy conditions

Skill Level Considerations:
- Beginner: Recommend 2-4ft waves, calm winds, gentle breaks
- Intermediate: Recommend 3-6ft waves, moderate conditions
- Advanced: Can handle 5-10ft+ waves, stronger winds

Respond in JSON format with these fields:
- recommendation: Concise surf advice (max 150 words)
- confidence: Float 0.0-1.0 (how confident you are in this recommendation)
- explanation: Detailed reasoning explaining the conditions and your advice (max 200 words)

Be friendly, enthusiastic, and use surf terminology appropriately. If conditions are poor, suggest alternative activities or best times to check back.
"""


async def call_openai_api(prompt: str) -> dict:
    """
    Call OpenAI API with the constructed prompt
    
    Args:
        prompt: Formatted prompt with surf data and user query
    
    Returns:
        Dictionary with AI response data
    """
    try:
        from openai import OpenAI
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            raise HTTPException(
                status_code=500, 
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY in environment."
            )
        
        # Initialize OpenAI client (v1.0+ API)
        client = OpenAI(api_key=api_key)
        
        logger.info(f"Calling OpenAI API with prompt length: {len(prompt)}")
        
        # Call GPT-4o (faster and more cost-effective than GPT-4)
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {
                    "role": "system",
                    "content": "You are SurfGPT, an expert surf forecasting AI. Always respond in valid JSON format with recommendation, confidence, and explanation fields."
                },
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            temperature=0.7,
            max_tokens=500,
            response_format={"type": "json_object"}
        )
        
        # Parse response
        ai_response = response.choices[0].message.content
        logger.info(f"OpenAI response received: {ai_response[:200]}...")
        
        # Parse JSON response
        import json
        parsed_response = json.loads(ai_response)
        
        return {
            "recommendation": parsed_response.get("recommendation", "No recommendation available"),
            "confidence": float(parsed_response.get("confidence", 0.5)),
            "explanation": parsed_response.get("explanation", "Analysis completed"),
        }
        
    except Exception as e:
        logger.error(f"Unexpected error calling OpenAI: {e}")
        raise HTTPException(status_code=500, detail=f"AI processing error: {str(e)}")


@router.post("/query", response_model=AIResponse)
async def ai_query(
    query: AIQuery,
    db: AsyncSession = Depends(get_db)
):
    """
    AI-powered surf query endpoint with location awareness
    
    Accepts natural language questions about surf conditions and returns
    intelligent recommendations based on real-time NOAA buoy data.
    
    Supports multiple location formats:
    - Location string: "western PR", "California", "Florida"
    - Coordinates: latitude=18.4, longitude=-67.2
    
    Example queries:
    - "Where should I surf tomorrow?" (location="western PR")
    - "Are the conditions good for a beginner right now?" (latitude=29.2, longitude=-79.9)
    - "What time is best to surf today?"
    - "Is the swell quality good?"
    
    Args:
        query: AIQuery object with user question and optional location/coordinates
        db: Database session
    
    Returns:
        AIResponse with recommendation, confidence score, explanation, and location info
    """
    try:
        logger.info(f"AI Query received: {query.query} (skill: {query.skill_level}, location: {query.location})")
        
        # Step 1: Determine which buoy to use based on location
        buoy = None
        if query.location or (query.latitude and query.longitude):
            buoy = await get_buoy_by_location(
                db,
                location=query.location,
                latitude=query.latitude,
                longitude=query.longitude
            )
            if buoy:
                logger.info(f"Selected buoy: {buoy.station_id} ({buoy.name}) in {buoy.region}")
            else:
                logger.warning(f"No buoy found for location: {query.location or f'({query.latitude}, {query.longitude})'}")
        
        # Fallback to default buoy if no location match
        if not buoy:
            buoy = await get_default_buoy(db)
            if buoy:
                logger.info(f"Using default buoy: {buoy.station_id} ({buoy.name})")
        
        # Step 2: Fetch recent surf data from selected buoy
        buoy_id = buoy.station_id if buoy else None
        surf_data = await fetch_recent_surf_data(db, buoy_id=buoy_id, hours=24)
        
        # Step 3: Build AI prompt with context
        prompt = build_ai_prompt(query.query, surf_data, query.skill_level)
        
        # Step 4: Call OpenAI API
        ai_response = await call_openai_api(prompt)
        
        # Step 5: Format and return response
        data_timestamp = surf_data.get("current", {}).get("timestamp") if surf_data["status"] == "success" else None
        
        response = AIResponse(
            query=query.query,
            recommendation=ai_response["recommendation"],
            confidence=ai_response["confidence"],
            explanation=ai_response["explanation"],
            data_timestamp=data_timestamp,
            station_used=buoy.station_id if buoy else None,
            region=buoy.region if buoy else None
        )
        
        logger.info(f"AI response generated with confidence: {response.confidence} (buoy: {response.station_used})")
        
        return response
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in AI query endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Internal server error: {str(e)}"
        )

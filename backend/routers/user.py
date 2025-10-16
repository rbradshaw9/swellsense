"""
SwellSense User Profile API
User account management and profile endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel, Field
from datetime import datetime
import logging
import os
from typing import Optional, List
from supabase import create_client, Client
from auth import verify_token, AuthUser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set - profile operations will fail")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)

# Initialize Supabase client
SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
    logger.warning("SUPABASE_URL or SUPABASE_SERVICE_KEY not set - profile operations will fail")
    supabase: Optional[Client] = None
else:
    supabase: Client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)


class UserPreferences(BaseModel):
    """User preferences model"""
    units: str = Field(default="imperial", pattern="^(imperial|metric)$")
    skill_level: str = Field(default="intermediate", pattern="^(beginner|intermediate|advanced|expert)$")
    board_type: str = Field(default="shortboard", pattern="^(shortboard|longboard|funboard|fish|gun)$")
    favorite_spots: List[str] = Field(default_factory=list)
    notifications: bool = True
    ai_persona: str = Field(default="experienced", pattern="^(beginner|experienced|expert|local)$")


class ExtendedUserProfile(BaseModel):
    """Extended user profile with personal info and preferences"""
    id: str
    email: str
    role: str
    username: Optional[str] = None
    name: Optional[str] = None
    home_spot: Optional[str] = None
    avatar_url: Optional[str] = None
    preferences: UserPreferences
    created_at: Optional[str] = None
    authenticated: bool = True


class UpdateProfileRequest(BaseModel):
    """Request model for updating user profile"""
    username: Optional[str] = Field(None, min_length=3, max_length=30, pattern="^[a-zA-Z0-9_-]+$")
    name: Optional[str] = Field(None, max_length=100)
    home_spot: Optional[str] = Field(None, max_length=100)
    avatar_url: Optional[str] = None
    preferences: Optional[UserPreferences] = None


class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    email: str
    role: str
    authenticated: bool = True


@router.get("/profile", response_model=ExtendedUserProfile)
async def get_profile(user: AuthUser = Depends(verify_token)):
    """
    Get current user's extended profile information including preferences
    
    Requires authentication via Supabase JWT token in Authorization header.
    Fetches user_profiles and user_preferences from Supabase.
    
    Args:
        user: Authenticated user from JWT token
    
    Returns:
        ExtendedUserProfile: User's complete profile and preferences
    
    Example:
        GET /api/user/profile
        Headers: Authorization: Bearer <supabase_jwt_token>
        
        Response:
        {
            "id": "uuid-here",
            "email": "surfer@example.com",
            "role": "authenticated",
            "username": "surferbro",
            "name": "John Doe",
            "home_spot": "Rincon",
            "preferences": {
                "units": "imperial",
                "skill_level": "intermediate",
                "board_type": "shortboard",
                "favorite_spots": ["Rincon", "Malibu"],
                "notifications": true,
                "ai_persona": "experienced"
            }
        }
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
    
    logger.info(f"Extended profile request from user: {user.email}")
    
    try:
        # Fetch user profile
        profile_response = supabase.table("user_profiles").select("*").eq("id", user.id).execute()
        profile_data = profile_response.data[0] if profile_response.data else {}
        
        # Fetch user preferences
        prefs_response = supabase.table("user_preferences").select("*").eq("user_id", user.id).execute()
        prefs_data = prefs_response.data[0] if prefs_response.data else {}
        
        # Build preferences object with defaults
        preferences = UserPreferences(
            units=prefs_data.get("units", "imperial"),
            skill_level=prefs_data.get("skill_level", "intermediate"),
            board_type=prefs_data.get("board_type", "shortboard"),
            favorite_spots=prefs_data.get("favorite_spots", []),
            notifications=prefs_data.get("notifications", True),
            ai_persona=prefs_data.get("ai_persona", "experienced")
        )
        
        return ExtendedUserProfile(
            id=user.id,
            email=user.email,
            role=user.role,
            username=profile_data.get("username"),
            name=profile_data.get("name"),
            home_spot=profile_data.get("home_spot"),
            avatar_url=profile_data.get("avatar_url"),
            preferences=preferences,
            created_at=profile_data.get("created_at"),
            authenticated=True
        )
    except Exception as e:
        logger.error(f"Error fetching profile: {e}")
        # Return basic profile if extended fetch fails
        return ExtendedUserProfile(
            id=user.id,
            email=user.email,
            role=user.role,
            preferences=UserPreferences(),
            authenticated=True
        )


@router.post("/profile")
async def update_profile(
    updates: UpdateProfileRequest,
    user: AuthUser = Depends(verify_token)
):
    """
    Update user profile and preferences
    
    Requires authentication. Updates user_profiles and user_preferences tables.
    Username must be unique across all users.
    
    Args:
        updates: Profile fields to update
        user: Authenticated user from JWT token
    
    Returns:
        dict: Success confirmation with updated profile
    
    Example:
        POST /api/user/profile
        Headers: Authorization: Bearer <supabase_jwt_token>
        Body:
        {
            "username": "surferbro",
            "name": "John Doe",
            "home_spot": "Rincon",
            "preferences": {
                "units": "metric",
                "skill_level": "advanced",
                "board_type": "shortboard"
            }
        }
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
    
    logger.info(f"Profile update request from user: {user.email}")
    
    try:
        # Check username uniqueness if provided
        if updates.username:
            existing = supabase.table("user_profiles").select("id").eq("username", updates.username).neq("id", user.id).execute()
            if existing.data:
                raise HTTPException(status_code=400, detail="Username already taken")
        
        # Update user_profiles
        profile_updates = {}
        if updates.username is not None:
            profile_updates["username"] = updates.username
        if updates.name is not None:
            profile_updates["name"] = updates.name
        if updates.home_spot is not None:
            profile_updates["home_spot"] = updates.home_spot
        if updates.avatar_url is not None:
            profile_updates["avatar_url"] = updates.avatar_url
        
        if profile_updates:
            supabase.table("user_profiles").upsert({
                "id": user.id,
                **profile_updates
            }).execute()
        
        # Update user_preferences
        if updates.preferences:
            prefs_dict = updates.preferences.dict()
            supabase.table("user_preferences").upsert({
                "user_id": user.id,
                **prefs_dict
            }).execute()
        
        return {
            "status": "success",
            "message": "Profile updated successfully",
            "user_id": user.id
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating profile: {e}")
        raise HTTPException(status_code=500, detail=f"Failed to update profile: {str(e)}")


@router.get("/check-username")
async def check_username_availability(username: str):
    """
    Check if a username is available
    
    Public endpoint (no auth required) to validate username uniqueness.
    
    Args:
        username: Username to check
    
    Returns:
        dict: Availability status
    
    Example:
        GET /api/user/check-username?username=surferbro
        
        Response:
        {
            "available": true,
            "username": "surferbro"
        }
    """
    if not supabase:
        raise HTTPException(status_code=500, detail="Supabase client not initialized")
    
    if len(username) < 3 or len(username) > 30:
        return {
            "available": False,
            "username": username,
            "reason": "Username must be 3-30 characters"
        }
    
    try:
        existing = supabase.table("user_profiles").select("id").eq("username", username).execute()
        available = len(existing.data) == 0
        
        return {
            "available": available,
            "username": username
        }
    except Exception as e:
        logger.error(f"Error checking username: {e}")
        raise HTTPException(status_code=500, detail="Failed to check username availability")


@router.get("/verify")
async def verify_auth(user: AuthUser = Depends(verify_token)):
    """
    Verify authentication token is valid
    
    Quick endpoint to check if user's token is still valid.
    
    Args:
        user: Authenticated user from JWT token
    
    Returns:
        dict: Confirmation of valid authentication
    
    Example:
        GET /api/user/verify
        Headers: Authorization: Bearer <supabase_jwt_token>
        
        Response:
        {
            "authenticated": true,
            "user_id": "uuid-here",
            "email": "surfer@example.com"
        }
    """
    return {
        "authenticated": True,
        "user_id": user.id,
        "email": user.email
    }

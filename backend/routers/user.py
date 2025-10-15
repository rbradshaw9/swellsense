"""
SwellSense User Profile API
User account management and profile endpoints
"""
from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from datetime import datetime
import logging
from auth import verify_token, AuthUser

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/user", tags=["user"])


class UserProfile(BaseModel):
    """User profile response model"""
    id: str
    email: str
    role: str
    authenticated: bool = True


@router.get("/profile", response_model=UserProfile)
async def get_profile(user: AuthUser = Depends(verify_token)):
    """
    Get current user's profile information
    
    Requires authentication via Supabase JWT token in Authorization header.
    
    Args:
        user: Authenticated user from JWT token
    
    Returns:
        UserProfile: User's profile information
    
    Example:
        GET /api/user/profile
        Headers: Authorization: Bearer <supabase_jwt_token>
        
        Response:
        {
            "id": "uuid-here",
            "email": "surfer@example.com",
            "role": "authenticated",
            "authenticated": true
        }
    """
    logger.info(f"Profile request from user: {user.email}")
    
    return UserProfile(
        id=user.id,
        email=user.email,
        role=user.role,
        authenticated=True
    )


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

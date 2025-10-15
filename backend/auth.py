"""
SwellSense Authentication Middleware
Verifies Supabase JWT tokens for protected routes
"""
from fastapi import Request, HTTPException, Depends
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import jwt
import os
import logging
from typing import Optional

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Security scheme for Swagger docs
security = HTTPBearer()

# Supabase JWT Secret (from your Supabase project settings -> API -> JWT Secret)
SUPABASE_JWT_SECRET = os.getenv("SUPABASE_JWT_SECRET")

if not SUPABASE_JWT_SECRET:
    logger.warning("SUPABASE_JWT_SECRET not set - authentication will fail")


class AuthUser:
    """Authenticated user model from JWT payload"""
    def __init__(self, user_id: str, email: str, role: str = "authenticated"):
        self.id = user_id
        self.email = email
        self.role = role

    def __repr__(self):
        return f"AuthUser(id={self.id}, email={self.email}, role={self.role})"


async def verify_token(
    credentials: HTTPAuthorizationCredentials = Depends(security)
) -> AuthUser:
    """
    Verify Supabase JWT token and extract user information
    
    Args:
        credentials: HTTP Authorization credentials with Bearer token
    
    Returns:
        AuthUser: Authenticated user object with id, email, and role
    
    Raises:
        HTTPException: 401 if token is invalid or missing
    
    Example:
        @router.get("/protected")
        async def protected_route(user: AuthUser = Depends(verify_token)):
            return {"user_id": user.id, "email": user.email}
    """
    if not SUPABASE_JWT_SECRET:
        logger.error("SUPABASE_JWT_SECRET not configured")
        raise HTTPException(
            status_code=500,
            detail="Authentication not configured"
        )

    token = credentials.credentials

    try:
        # Decode JWT token using Supabase JWT secret
        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )

        # Extract user information from payload
        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "authenticated")

        if not user_id:
            raise HTTPException(
                status_code=401,
                detail="Invalid token: missing user ID"
            )

        logger.info(f"Authenticated user: {email} ({user_id})")
        
        return AuthUser(user_id=user_id, email=email, role=role)

    except jwt.ExpiredSignatureError:
        logger.warning("Token expired")
        raise HTTPException(
            status_code=401,
            detail="Token has expired"
        )
    except jwt.InvalidTokenError as e:
        logger.warning(f"Invalid token: {e}")
        raise HTTPException(
            status_code=401,
            detail="Invalid authentication token"
        )
    except Exception as e:
        logger.error(f"Authentication error: {e}")
        raise HTTPException(
            status_code=401,
            detail="Authentication failed"
        )


async def optional_verify_token(
    request: Request
) -> Optional[AuthUser]:
    """
    Optional authentication - extracts user if token present, returns None if not
    
    Useful for routes that have different behavior for authenticated vs anonymous users
    
    Args:
        request: FastAPI request object
    
    Returns:
        Optional[AuthUser]: User if authenticated, None otherwise
    
    Example:
        @router.get("/optional")
        async def optional_route(user: Optional[AuthUser] = Depends(optional_verify_token)):
            if user:
                return {"message": f"Hello {user.email}"}
            return {"message": "Hello anonymous user"}
    """
    auth_header = request.headers.get("Authorization")
    
    if not auth_header or not auth_header.startswith("Bearer "):
        return None

    try:
        token = auth_header.split("Bearer ")[-1]
        
        if not SUPABASE_JWT_SECRET:
            return None

        payload = jwt.decode(
            token,
            SUPABASE_JWT_SECRET,
            algorithms=["HS256"],
            audience="authenticated"
        )

        user_id = payload.get("sub")
        email = payload.get("email")
        role = payload.get("role", "authenticated")

        if user_id:
            return AuthUser(user_id=user_id, email=email, role=role)
        
        return None

    except Exception as e:
        logger.debug(f"Optional auth failed: {e}")
        return None

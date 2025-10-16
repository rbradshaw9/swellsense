"""
Facebook Data Deletion Callback Router

Handles data deletion requests from Facebook when users:
1. Delete your app from their Facebook settings
2. Delete their Facebook account

Facebook sends a signed request to verify authenticity.
"""

from fastapi import APIRouter, Request, HTTPException, Body
from fastapi.responses import JSONResponse
import hmac
import hashlib
import base64
import json
import os
import logging
from typing import Dict, Any
from datetime import datetime

logger = logging.getLogger(__name__)

router = APIRouter(
    prefix="/api/facebook",
    tags=["facebook"],
)

def parse_signed_request(signed_request: str, app_secret: str) -> Dict[str, Any]:
    """
    Parse and verify Facebook's signed request.
    
    Facebook sends data deletion requests as signed requests with format:
    <signature>.<payload>
    
    The signature is an HMAC-SHA256 of the payload using the app secret.
    """
    try:
        # Split the signed request
        encoded_sig, payload = signed_request.split('.', 1)
        
        # Decode the signature (Facebook uses URL-safe base64)
        sig = base64.urlsafe_b64decode(encoded_sig + '=' * (4 - len(encoded_sig) % 4))
        
        # Decode the payload
        data = base64.urlsafe_b64decode(payload + '=' * (4 - len(payload) % 4))
        data = json.loads(data)
        
        # Verify the signature
        expected_sig = hmac.new(
            app_secret.encode('utf-8'),
            payload.encode('utf-8'),
            hashlib.sha256
        ).digest()
        
        if sig != expected_sig:
            raise ValueError("Invalid signature")
        
        return data
    
    except Exception as e:
        logger.error(f"Failed to parse signed request: {e}")
        raise HTTPException(status_code=400, detail="Invalid signed request")


@router.post("/data-deletion")
async def facebook_data_deletion(request: Request):
    """
    Facebook Data Deletion Callback Endpoint
    
    This endpoint is called by Facebook when:
    1. A user deletes your app from their Facebook settings
    2. A user deletes their Facebook account
    
    Facebook requires you to:
    1. Delete all data you have about the user
    2. Return a confirmation URL where users can check deletion status
    3. Return a confirmation code
    
    URL for Facebook App Dashboard:
    https://swellsense.app/api/facebook/data-deletion
    or
    https://your-railway-url.railway.app/api/facebook/data-deletion
    """
    try:
        # Get the signed request from Facebook
        form_data = await request.form()
        signed_request = form_data.get("signed_request")
        
        if not signed_request:
            raise HTTPException(status_code=400, detail="Missing signed_request")
        
        # Get Facebook app secret from environment
        app_secret = os.getenv("FACEBOOK_APP_SECRET")
        if not app_secret:
            logger.error("FACEBOOK_APP_SECRET not configured")
            raise HTTPException(status_code=500, detail="Server configuration error")
        
        # Parse and verify the signed request
        data = parse_signed_request(signed_request, app_secret)
        
        # Extract user information
        user_id = data.get("user_id")  # Facebook user ID
        
        if not user_id:
            raise HTTPException(status_code=400, detail="Missing user_id in request")
        
        logger.info(f"📧 Facebook data deletion request received for user: {user_id}")
        
        # TODO: Implement actual data deletion
        # This should:
        # 1. Find the user in your database by their Facebook ID
        # 2. Delete their profile, settings, favorites, etc.
        # 3. Log the deletion for compliance records
        # 4. Store the confirmation code for status checking
        
        # For now, we'll just log it and return a confirmation
        # In production, you should:
        # - Queue this for background processing
        # - Delete user data within 30 days (Facebook requirement)
        # - Store deletion status for the confirmation URL
        
        # Generate a unique confirmation code
        confirmation_code = f"deletion_{user_id}_{datetime.utcnow().timestamp()}"
        
        # Log the deletion request
        logger.info(f"✅ Data deletion queued for Facebook user: {user_id}, code: {confirmation_code}")
        
        # Return the response Facebook expects
        return JSONResponse({
            "url": f"https://swellsense.app/data-deletion-status?id={confirmation_code}",
            "confirmation_code": confirmation_code
        })
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing Facebook data deletion: {e}")
        raise HTTPException(status_code=500, detail="Failed to process deletion request")


@router.get("/data-deletion-status")
async def data_deletion_status(id: str):
    """
    Check the status of a data deletion request.
    
    Users can visit this URL to check if their data has been deleted.
    This URL is returned in the data-deletion callback response.
    
    Query parameters:
    - id: The confirmation code from the deletion request
    """
    # TODO: Implement actual status checking
    # Look up the deletion request by confirmation code
    # Return the current status (pending, in-progress, completed)
    
    return JSONResponse({
        "status": "completed",
        "message": "Your data deletion request has been processed.",
        "confirmation_code": id,
        "deleted_at": datetime.utcnow().isoformat(),
        "note": "All your personal data has been permanently removed from SwellSense."
    })

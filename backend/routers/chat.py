"""
SwellSense AI Chat API endpoint
Conversational surf assistant using OpenAI
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Literal
from datetime import datetime
import os
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/ai", tags=["ai-chat"])


class ChatMessage(BaseModel):
    """Single chat message"""
    role: Literal["user", "assistant", "system"]
    content: str


class ChatRequest(BaseModel):
    """Request model for chat endpoint"""
    messages: List[ChatMessage]


class ChatResponse(BaseModel):
    """Response model for chat endpoint"""
    reply: str
    timestamp: str


@router.post("/chat", response_model=ChatResponse)
async def chat(request: ChatRequest):
    """
    SwellSense conversational AI surf assistant endpoint
    
    Accepts a conversation history and returns the AI's response.
    Uses OpenAI GPT-4o-mini to provide friendly, knowledgeable surf advice.
    
    The assistant can:
    - Answer questions about surf conditions
    - Compare different surf spots
    - Explain surf terminology and concepts
    - Give board and timing recommendations
    - Provide safety advice
    
    Args:
        request: ChatRequest with message history
    
    Returns:
        ChatResponse with AI reply and timestamp
    
    Example:
        POST /api/ai/chat
        {
            "messages": [
                {"role": "user", "content": "What's the best time to surf Domes tomorrow?"}
            ]
        }
    """
    try:
        logger.info(f"Chat request received with {len(request.messages)} messages")
        
        # Validate message history
        if not request.messages:
            raise HTTPException(
                status_code=400,
                detail="Message history cannot be empty"
            )
        
        # Log last user message for debugging
        last_user_msg = next((m for m in reversed(request.messages) if m.role == "user"), None)
        if last_user_msg:
            logger.debug(f"User message: {last_user_msg.content[:100]}...")
        
        # Import OpenAI client
        try:
            from openai import OpenAI
        except ImportError:
            logger.error("OpenAI package not installed")
            raise HTTPException(
                status_code=500,
                detail="OpenAI integration not available"
            )
        
        # Get API key from environment
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            logger.error("OPENAI_API_KEY not found in environment")
            raise HTTPException(
                status_code=500,
                detail="OpenAI API key not configured. Please set OPENAI_API_KEY in environment."
            )
        
        # Initialize OpenAI client
        client = OpenAI(api_key=api_key)
        
        # System prompt for SwellSense chat assistant
        system_prompt = """You are SwellSense, a friendly surf forecasting assistant for Puerto Rico and global surf spots.

You help surfers by:
- Answering questions about surf conditions conversationally
- Comparing different surf locations (Domes, Tres Palmas, Jobos, Crash Boat, etc.)
- Explaining surf concepts and terminology in beginner-friendly language
- Giving board recommendations and timing advice
- Providing safety tips for different skill levels

Use surfer terminology naturally: 'glassy', 'offshore', 'onshore', 'clean', 'choppy', 'sets', 'lineup', 'barrels', 'close-outs', etc.

Be enthusiastic and encouraging, like chatting with a knowledgeable local surfer friend. Keep responses concise but informative (2-4 paragraphs max unless asked for details).

When discussing Puerto Rico spots:
- **Rincón (West Coast)**: Domes, Tres Palmas, Maria's - world-class winter waves
- **Isabela (Northwest)**: Jobos, Middles, Shacks - consistent year-round
- **Aguadilla**: Crash Boat, Gas Chambers, Wilderness - varied skill levels
- **East Coast**: Pine Grove, La Pared - less crowded alternatives

Always consider:
- Skill level (beginner/intermediate/advanced)
- Safety first (strong currents, reef breaks, size warnings)
- Best times (tides, winds, swell direction)
- Seasonal patterns (winter vs summer swells)"""

        # Build message history with system prompt
        messages = [{"role": "system", "content": system_prompt}]
        
        # Add conversation history
        for msg in request.messages:
            messages.append({
                "role": msg.role,
                "content": msg.content
            })
        
        logger.info(f"Calling OpenAI with {len(messages)} messages")
        
        # Call OpenAI API with timeout
        try:
            response = client.chat.completions.create(
                model="gpt-4o-mini",
                messages=messages,
                temperature=0.8,  # Slightly higher for more conversational tone
                max_tokens=600,
                timeout=30  # 30 second timeout
            )
        except Exception as openai_error:
            logger.error(f"OpenAI API error: {openai_error}")
            if "timeout" in str(openai_error).lower():
                raise HTTPException(
                    status_code=504,
                    detail="AI response timeout. Please try again."
                )
            raise HTTPException(
                status_code=500,
                detail=f"OpenAI API error: {str(openai_error)}"
            )
        
        # Extract AI response
        ai_reply = response.choices[0].message.content
        
        if not ai_reply:
            logger.error("Empty response from OpenAI")
            raise HTTPException(
                status_code=500,
                detail="Received empty response from AI"
            )
        
        logger.info(f"AI response generated: {len(ai_reply)} characters")
        logger.debug(f"AI reply: {ai_reply[:200]}...")
        
        return ChatResponse(
            reply=ai_reply,
            timestamp=datetime.utcnow().isoformat() + "Z"
        )
        
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    
    except Exception as e:
        logger.error(f"Unexpected error in chat endpoint: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Chat error: {str(e)}"
        )

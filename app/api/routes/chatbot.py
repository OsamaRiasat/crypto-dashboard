from fastapi import APIRouter, Body, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
from app.api.services.chatbot_prompt import CRYPTO_ASSISTANT_PROMPT
from app.api.services.llm_service import llm_service
from app.utils.helpers import get_logger

# Create logger
logger = get_logger(__name__)

# Create router for chatbot endpoints
router = APIRouter(prefix="/chatbot", tags=["chatbot"])

# Define request model
class ChatRequest(BaseModel):
    message: str
    user_id: Optional[str] = None

# Define response model
class ChatResponse(BaseModel):
    response: str

@router.post("/", response_model=ChatResponse)
async def crypto_chatbot(request: ChatRequest):
    """
    Chatbot endpoint that provides guidance on cryptocurrency topics using GPT-4.
    
    This endpoint accepts user messages and returns helpful information about
    cryptocurrencies, trading, portfolio management, and related topics using
    the OpenAI GPT-4 model guided by a specialized crypto assistant prompt.
    """
    try:
        # Log incoming request (without sensitive data)
        logger.info(f"Received chatbot request: {len(request.message)} chars")
        
        # Process the user message
        user_message = request.message.strip()
        user_id = request.user_id or "anonymous"
        
        # Generate a response using GPT-4
        llm_response = await llm_service.generate_response(
            prompt=CRYPTO_ASSISTANT_PROMPT,
            user_message=user_message,
            max_tokens=500,
            temperature=0.7
        )
        
        # If we got a valid response from the LLM, return it
        if llm_response:
            logger.info(f"Generated response using GPT-4 for user {user_id}")
            return ChatResponse(response=llm_response)
        
        # If LLM failed, check if it's due to missing API key
        if not llm_service.api_key:
            logger.error(f"LLM generation failed for user {user_id} - API key not set")
            return ChatResponse(
                response="I'm sorry, but the OpenAI API key is not configured. Please add your API key to the .env file to enable AI-powered responses."
            )
        else:
            # Other LLM errors
            logger.error(f"LLM generation failed for user {user_id}")
            return ChatResponse(
                response="I'm sorry, I'm having trouble generating a response right now. Please try again in a moment."
            )
        
    except Exception as e:
        # Log the error
        logger.error(f"Error processing chatbot request: {str(e)}")
        # Return a friendly error message
        raise HTTPException(
            status_code=500,
            detail="Sorry, I'm having trouble processing your request right now. Please try again later."
        )
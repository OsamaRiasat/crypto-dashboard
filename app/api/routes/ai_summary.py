"""
AI Summary API Routes

Provides endpoints for generating AI-driven portfolio strategy summaries.
"""

from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.api.models.user import User
from app.api.schemas.strategy import StrategySummaryResponse
from app.api.services.strategy_summary import strategy_summary_service
from app.core.db import get_db
from app.core.security import get_current_user
from app.utils.helpers import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/ai", tags=["ai"])


@router.post("/strategy-summary", response_model=StrategySummaryResponse)
async def generate_strategy_summary(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Generate an AI-written summary of the user's portfolio strategy.
    
    This endpoint:
    - Analyzes user's onboarding data (intent, experience, risk profile)
    - Compares target vs current tier allocations
    - Includes goal progress if available
    - Returns a neutral, explanatory summary (max 150 words)
    
    Requirements:
    - User must have completed onboarding
    - User must have risk allocation configured
    - OpenAI API key must be configured
    
    Returns:
    - summary_text: AI-generated summary (informational only, not advice)
    - generated_at: ISO timestamp
    
    Note: This is informational only and not financial advice.
    """
    try:
        user_id = current_user.id
        
        # Generate summary
        result = await strategy_summary_service.generate_summary(db, user_id)
        
        if not result:
            raise HTTPException(
                status_code=400,
                detail="Cannot generate summary. Please ensure you have completed onboarding and configured your portfolio strategy."
            )
        
        return StrategySummaryResponse(
            summary_text=result["summary_text"],
            generated_at=result["generated_at"]
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating strategy summary: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error generating strategy summary: {str(e)}"
        )

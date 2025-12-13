"""
AI Strategy Summary Service

Generates AI-written summaries of user portfolio state relative to their
onboarding-defined strategy. Informational only - does not provide advice.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from loguru import logger

from app.api.models.user_onboarding import UserOnboarding
from app.api.models.user_risk_allocation import UserRiskAllocation
from app.api.models.user_goal import UserGoal
from app.api.models.user_contribution_plan import UserContributionPlan
from app.api.services.llm_service import llm_service


class StrategySummaryService:
    """Service for generating AI portfolio strategy summaries."""
    
    # System prompt for AI summary generation
    SYSTEM_PROMPT = """You are a neutral portfolio analysis assistant. Your role is to describe the user's current portfolio state relative to their defined strategy in an explanatory, non-directive manner.

CRITICAL RULES:
1. Maximum 150 words
2. Be factual and neutral - explain, don't advise
3. NEVER use: "should", "recommend", "buy", "sell", "must", "need to"
4. NEVER predict prices or returns
5. NEVER use persuasive or urgent language
6. Describe alignment vs deviation objectively
7. Explain trade-offs (e.g. volatility vs growth) without recommending action
8. If goal data exists, mention progress status factually
9. Use neutral descriptors: "shows", "indicates", "reflects", "demonstrates"

Focus on:
- Current allocation vs target allocation (factual comparison)
- How the allocation relates to their stated intent and risk profile
- Trade-offs inherent in their current setup
- Goal progress if applicable (factual status only)
- Recent performance context (observation, not prediction)"""

    def __init__(self):
        """Initialize the strategy summary service."""
        self.llm_service = llm_service

    def _build_context(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Build structured context object from user's strategy data.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Context dictionary or None if insufficient data
        """
        try:
            # Get onboarding data
            onboarding = db.query(UserOnboarding).filter(
                UserOnboarding.user_id == user_id
            ).first()
            
            if not onboarding:
                logger.info(f"User {user_id} has not completed onboarding")
                return None
            
            # Get risk allocation
            risk_alloc = db.query(UserRiskAllocation).filter(
                UserRiskAllocation.user_id == user_id
            ).first()
            
            if not risk_alloc:
                logger.info(f"User {user_id} has no risk allocation")
                return None
            
            # Get goals (optional)
            goals = db.query(UserGoal).filter(
                UserGoal.user_id == user_id
            ).all()
            
            # Get contribution plan (optional)
            contribution = db.query(UserContributionPlan).filter(
                UserContributionPlan.user_id == user_id
            ).first()
            
            # Build context
            context = {
                "intent": onboarding.intent.value if onboarding.intent else "not specified",
                "experience": onboarding.experience.value if onboarding.experience else "not specified",
                "allocation_preset": onboarding.allocation_preset.value if onboarding.allocation_preset else "not specified",
                "target_allocation": {
                    "collateral": risk_alloc.collateral_pct,
                    "growth": risk_alloc.growth_pct,
                    "wildcard": risk_alloc.wildcard_pct
                },
                "portfolio_size": onboarding.portfolio_size,
                "goals": [],
                "contribution": None
            }
            
            # Add goals if available
            if goals:
                context["goals"] = [
                    {
                        "name": goal.name,
                        "target_amount": float(goal.target_amount),
                        "months": goal.months
                    }
                    for goal in goals
                ]
            
            # Add contribution plan if available
            if contribution:
                context["contribution"] = {
                    "amount": float(contribution.amount),
                    "frequency": contribution.frequency.value
                }
            
            return context
            
        except Exception as e:
            logger.error(f"Error building context for user {user_id}: {str(e)}")
            return None

    def _format_user_message(self, context: Dict[str, Any]) -> str:
        """
        Format context into a user message for the LLM.
        
        Args:
            context: Structured context dictionary
            
        Returns:
            Formatted message string
        """
        msg_parts = []
        
        # Basic strategy info
        msg_parts.append(f"User Intent: {context['intent']}")
        msg_parts.append(f"Experience Level: {context['experience']}")
        msg_parts.append(f"Risk Profile: {context['allocation_preset']}")
        
        # Target allocation
        alloc = context['target_allocation']
        msg_parts.append(f"Target Allocation: {alloc['collateral']}% Collateral, {alloc['growth']}% Growth, {alloc['wildcard']}% Wildcard")
        
        # Portfolio size
        if context.get('portfolio_size'):
            msg_parts.append(f"Portfolio Size: ${context['portfolio_size']:,.0f}")
        
        # For now, we'll use target allocation as current (until we have real portfolio data)
        # In a real implementation, you would fetch actual current allocations from wallet data
        msg_parts.append(f"Current Allocation: ~{alloc['collateral']}% Collateral, ~{alloc['growth']}% Growth, ~{alloc['wildcard']}% Wildcard")
        
        # Goals
        if context.get('goals'):
            msg_parts.append("\nGoals:")
            for goal in context['goals']:
                msg_parts.append(f"- {goal['name']}: ${goal['target_amount']:,.0f} in {goal['months']} months")
        
        # Contributions
        if context.get('contribution'):
            contrib = context['contribution']
            msg_parts.append(f"\nContributions: ${contrib['amount']:.2f} {contrib['frequency']}")
        
        msg_parts.append("\nGenerate a neutral, factual summary (max 150 words) describing this portfolio strategy.")
        
        return "\n".join(msg_parts)

    async def generate_summary(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Generate AI strategy summary for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with summary_text and generated_at, or None if cannot generate
        """
        try:
            # Build context
            context = self._build_context(db, user_id)
            if not context:
                logger.warning(f"Cannot generate summary for user {user_id}: insufficient data")
                return None
            
            # Format message
            user_message = self._format_user_message(context)
            
            # Generate summary using LLM
            summary_text = await self.llm_service.generate_response(
                prompt=self.SYSTEM_PROMPT,
                user_message=user_message,
                max_tokens=250,  # ~150 words
                temperature=0.5  # Lower temperature for more factual output
            )
            
            if not summary_text:
                logger.error(f"LLM service returned no summary for user {user_id}")
                return None
            
            # Return result
            return {
                "summary_text": summary_text.strip(),
                "generated_at": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error generating summary for user {user_id}: {str(e)}")
            return None


# Singleton instance
strategy_summary_service = StrategySummaryService()

"""
Strategy Drift Service

Calculates tier-level drift between target and current portfolio allocations.
Informational only - does not provide recommendations.
"""

from typing import Optional, Dict, Any
from datetime import datetime, timezone
from sqlalchemy.orm import Session
from loguru import logger

from app.api.models.user_risk_allocation import UserRiskAllocation
from app.api.models.user_selected_asset import UserSelectedAsset
from app.api.services.portfolio_categorization import portfolio_categorization
from app.api.models.enums import Layer


class StrategyDriftService:
    """Service for calculating portfolio strategy drift."""
    
    def __init__(self):
        """Initialize the strategy drift service."""
        self.portfolio_categorization = portfolio_categorization

    async def _get_current_allocations(self, user_id: int, db: Session) -> Optional[Dict[str, int]]:
        """
        Calculate current tier allocations from actual portfolio holdings.
        
        Args:
            user_id: User ID
            db: Database session
            
        Returns:
            Dictionary with tier percentages or None if insufficient data
        """
        try:
            # Use portfolio categorization service to get tier breakdown
            categorized_data = await self.portfolio_categorization.get_categorized_portfolio()
            
            if not categorized_data or categorized_data.get('total_value', 0) <= 0:
                logger.info(f"User {user_id} has no portfolio value")
                return None
            
            # Extract tier percentages from categorized data
            tiers = categorized_data.get('tiers', [])
            
            current_allocations = {
                "collateral": 0,
                "growth": 0,
                "wildcard": 0
            }
            
            for tier in tiers:
                tier_name = tier.get('tier', '').lower()
                percentage = tier.get('percentage', 0.0)
                
                if tier_name in current_allocations:
                    current_allocations[tier_name] = round(percentage)
            
            return current_allocations
            
        except Exception as e:
            logger.error(f"Error calculating current allocations for user {user_id}: {str(e)}")
            return None

    async def calculate_drift(self, db: Session, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Calculate strategy drift for a user.
        
        Args:
            db: Database session
            user_id: User ID
            
        Returns:
            Dictionary with target, current, drift, and last_updated or None
        """
        try:
            # Get target allocation from risk_allocations table
            risk_alloc = db.query(UserRiskAllocation).filter(
                UserRiskAllocation.user_id == user_id
            ).first()
            
            if not risk_alloc:
                logger.info(f"User {user_id} has no risk allocation configured")
                return None
            
            target = {
                "collateral": risk_alloc.collateral_pct,
                "growth": risk_alloc.growth_pct,
                "wildcard": risk_alloc.wildcard_pct
            }
            
            # Get current allocations from portfolio
            current_alloc = await self._get_current_allocations(user_id, db)
            
            # If we can't calculate current allocation, use target as approximation
            # This handles the case where user has set strategy but hasn't connected wallets yet
            if current_alloc is None:
                # Return target values as current (zero drift)
                current = {
                    "collateral": risk_alloc.collateral_pct,
                    "growth": risk_alloc.growth_pct,
                    "wildcard": risk_alloc.wildcard_pct
                }
            else:
                current = current_alloc
            
            # Calculate drift (current - target)
            drift = {
                "collateral": current["collateral"] - target["collateral"],
                "growth": current["growth"] - target["growth"],
                "wildcard": current["wildcard"] - target["wildcard"]
            }
            
            return {
                "target": target,
                "current": current,
                "drift": drift,
                "last_updated": datetime.now(timezone.utc)
            }
            
        except Exception as e:
            logger.error(f"Error calculating drift for user {user_id}: {str(e)}")
            return None


# Singleton instance
strategy_drift_service = StrategyDriftService()

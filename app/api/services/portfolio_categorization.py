"""
Portfolio Categorization Service

Handles categorization of portfolio assets into strategy tiers
and provides tier-based analytics.
"""

from typing import Dict, List, Any
from datetime import datetime
from loguru import logger

from app.api.services.portfolio import portfolio_service
from lib.strategy_categorization import categorize_asset


class PortfolioCategorization:
    """Service for categorizing portfolio assets by strategy tier."""
    
    def __init__(self):
        """Initialize the portfolio categorization service."""
        self.portfolio_service = portfolio_service
    
    async def get_categorized_portfolio(self) -> Dict[str, Any]:
        """
        Get portfolio data categorized by strategy tiers.
        
        Returns:
            Dictionary containing tiers with assets, percentages, and totals
            
        Raises:
            Exception: If portfolio data cannot be retrieved or categorized
        """
        try:
            # Get portfolio summary
            portfolio_data = await self.portfolio_service.get_portfolio_summary()
            
            if not portfolio_data or portfolio_data.total_portfolio_value_usd <= 0:
                return self._empty_categorization()
            
            # Collect all assets from wallets
            all_assets = self._collect_assets(portfolio_data.wallets)
            
            if not all_assets:
                return self._empty_categorization()
            
            total_value = portfolio_data.total_portfolio_value_usd
            
            # Categorize assets by tier
            tier_data = self._categorize_assets(all_assets)
            
            # Calculate tier breakdowns
            tiers = self._calculate_tier_breakdowns(tier_data, total_value)
            
            return {
                "tiers": tiers,
                "total_value": total_value,
                "last_updated": portfolio_data.last_updated
            }
            
        except Exception as e:
            logger.error(f"Error categorizing portfolio: {str(e)}")
            raise
    
    def _empty_categorization(self) -> Dict[str, Any]:
        """Return empty categorization structure."""
        return {
            "tiers": [
                {"tier": "Collateral", "percentage": 0.0, "total_value": 0.0, "assets": []},
                {"tier": "Growth", "percentage": 0.0, "total_value": 0.0, "assets": []},
                {"tier": "Wildcard", "percentage": 0.0, "total_value": 0.0, "assets": []},
            ],
            "total_value": 0.0,
            "last_updated": datetime.utcnow().isoformat() + "Z"
        }
    
    def _collect_assets(self, wallets: List[Any]) -> List[Dict[str, Any]]:
        """Collect all assets from wallet data."""
        all_assets = []
        for wallet in wallets:
            for asset in wallet.assets:
                all_assets.append({
                    'symbol': asset['asset'],
                    'amount': asset['balance'],
                    'value': asset['value_usd']
                })
        return all_assets
    
    def _categorize_assets(self, assets: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize assets into tiers."""
        tier_data = {
            "Collateral": [],
            "Growth": [],
            "Wildcard": []
        }
        
        for asset in assets:
            tier = categorize_asset(asset['symbol'])
            tier_data[tier].append({
                'symbol': asset['symbol'],
                'amount': asset['amount'],
                'value': asset['value'],
                'tier': tier
            })
        
        return tier_data
    
    def _calculate_tier_breakdowns(
        self, 
        tier_data: Dict[str, List[Dict[str, Any]]], 
        total_value: float
    ) -> List[Dict[str, Any]]:
        """Calculate tier breakdowns with percentages and totals."""
        tiers = []
        
        for tier_name in ["Collateral", "Growth", "Wildcard"]:
            tier_assets = tier_data[tier_name]
            tier_total = sum(asset['value'] for asset in tier_assets)
            tier_percentage = (tier_total / total_value * 100) if total_value > 0 else 0.0
            
            tiers.append({
                "tier": tier_name,
                "percentage": round(tier_percentage, 1),
                "total_value": tier_total,
                "assets": tier_assets
            })
        
        return tiers


# Singleton instance
portfolio_categorization = PortfolioCategorization()

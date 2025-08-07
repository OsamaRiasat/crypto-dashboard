from fastapi import APIRouter, HTTPException

from app.api.services.portfolio import portfolio_service
from app.api.models.portfolio import PortfolioSummary

router = APIRouter(prefix="/portfolio", tags=["portfolio"])

@router.get("/summary", response_model=PortfolioSummary)
async def get_portfolio_summary():
    """Get complete portfolio summary with total value and connected wallets count"""
    try:
        portfolio_data = await portfolio_service.get_portfolio_summary()
        return portfolio_data
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching portfolio summary: {str(e)}")

@router.get("/total-value")
async def get_total_portfolio_value():
    """Get just the total portfolio value across all wallets"""
    try:
        portfolio_data = await portfolio_service.get_portfolio_summary()
        return {
            "total_portfolio_value_usd": portfolio_data.total_portfolio_value_usd,
            "connected_wallets_count": portfolio_data.connected_wallets_count,
            "last_updated": portfolio_data.last_updated
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error fetching total portfolio value: {str(e)}")
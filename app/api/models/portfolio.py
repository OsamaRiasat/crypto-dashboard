from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class WalletInfo(BaseModel):
    wallet_type: str  # 'kucoin', 'binance', 'coinbase'
    connected: bool
    total_value_usd: float
    assets: List[Dict[str, Any]]
    error: Optional[str] = None

class PortfolioSummary(BaseModel):
    total_portfolio_value_usd: float
    connected_wallets_count: int
    wallets: List[WalletInfo]
    last_updated: str
    
    class Config:
        schema_extra = {
            "example": {
                "total_portfolio_value_usd": 15000.50,
                "connected_wallets_count": 2,
                "wallets": [
                    {
                        "wallet_type": "kucoin",
                        "connected": True,
                        "total_value_usd": 10000.25,
                        "assets": [
                            {"asset": "BTC", "balance": 0.5, "value_usd": 25000.0},
                            {"asset": "ETH", "balance": 2.0, "value_usd": 4000.0}
                        ]
                    },
                    {
                        "wallet_type": "binance",
                        "connected": True,
                        "total_value_usd": 5000.25,
                        "assets": [
                            {"asset": "BTC", "balance": 0.1, "value_usd": 5000.0}
                        ]
                    }
                ],
                "last_updated": "2024-01-15T10:30:00Z"
            }
        }
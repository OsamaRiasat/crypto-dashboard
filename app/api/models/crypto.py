from pydantic import BaseModel
from typing import Dict, Optional, List, Any

# CoinGecko Models
class CoinData(BaseModel):
    name: str
    symbol: str
    current_price: float
    market_cap: float
    market_cap_rank: int
    high_24h: Optional[float] = None
    low_24h: Optional[float] = None
    volume_24h: Optional[float] = None
    
    class Config:
        schema_extra = {
            "example": {
                "name": "Bitcoin",
                "symbol": "btc",
                "current_price": 50000.0,
                "market_cap": 1000000000000.0,
                "market_cap_rank": 1,
                "high_24h": 51000.0,
                "low_24h": 49000.0,
                "volume_24h": 30000000000.0
            }
        }

# KuCoin Models
class KuCoinAccount(BaseModel):
    id: str
    currency: str
    type: str
    balance: str
    available: str
    holds: str
    
    class Config:
        schema_extra = {
            "example": {
                "id": "5bd6e9286d99522a52e458de",
                "currency": "BTC",
                "type": "main",
                "balance": "0.00000000",
                "available": "0.00000000",
                "holds": "0.00000000"
            }
        }

class KuCoinKeyInfo(BaseModel):
    userId: str
    subName: str
    remarks: Optional[str] = None
    apiKey: str
    createAt: int
    permissions: List[Dict[str, Any]]
    ipRestrict: str
    
    class Config:
        schema_extra = {
            "example": {
                "userId": "5c2b99f4a18397029283d5a0",
                "subName": "",
                "remarks": "API Key for trading",
                "apiKey": "5c2b99f4a18397029283d5a0",
                "createAt": 1546391044000,
                "permissions": [
                    {"permissionType": "General", "ipWhitelist": "*"}
                ],
                "ipRestrict": "false"
            }
        }
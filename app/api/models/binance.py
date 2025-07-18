from pydantic import BaseModel
from typing import List, Dict, Any, Optional

class BinanceBalance(BaseModel):
    asset: str
    free: float
    locked: float

class BinanceTransaction(BaseModel):
    coin: str
    amount: float
    status: str

class BinanceAccount(BaseModel):
    balances: List[BinanceBalance]

    class Config:
        schema_extra = {
            "example": {
                "balances": [
                    {
                        "asset": "BTC",
                        "free": 0.01234567,
                        "locked": 0.0
                    },
                    {
                        "asset": "ETH",
                        "free": 0.98765432,
                        "locked": 0.1
                    }
                ]
            }
        }
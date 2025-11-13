from pydantic import BaseModel, Field
from typing import List, Dict, Any, Optional
from app.api.models.db import Intent, ExperienceLevel, AllocationPreset

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

# --- Requests / Responses ---

class PortfolioSizeUpdate(BaseModel):
    portfolio_size: int = Field(ge=0, description="Portfolio size in USD (non-negative)")

class PortfolioSizeResponse(BaseModel):
    user_id: int
    portfolio_size: int
    
    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "portfolio_size": 25000
            }
        }

# --- Intent Requests / Responses ---

class UserIntentUpdate(BaseModel):
    intent: Intent = Field(description="Onboarding intent: growth | tax | learning | fun")

class UserIntentResponse(BaseModel):
    user_id: int
    intent: Intent

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "intent": "growth"
            }
        }

# --- Combined Onboarding Update ---

class OnboardingUpdate(BaseModel):
    portfolio_size: Optional[int] = Field(default=None, ge=0, description="Portfolio size in USD (non-negative)")
    intent: Optional[Intent] = Field(default=None, description="Onboarding intent: growth | tax | learning | fun")
    experience: Optional[ExperienceLevel] = Field(default=None, description="Experience level: beginner | intermediate | advanced")
    allocation_preset: Optional[AllocationPreset] = Field(default=None, description="Allocation preset: Conservative | Moderate | Aggressive | YOLO")
    
class RiskAllocationUpdate(BaseModel):
    collateral_pct: Optional[int] = Field(default=None, ge=0, le=100, description="Collateral layer percentage (0–100)")
    growth_pct: Optional[int] = Field(default=None, ge=0, le=100, description="Growth layer percentage (0–100)")
    wildcard_pct: Optional[int] = Field(default=None, ge=0, le=100, description="Wildcard layer percentage (0–100)")

class OnboardingUpdate(BaseModel):
    portfolio_size: Optional[int] = Field(default=None, ge=0, description="Portfolio size in USD (non-negative)")
    intent: Optional[Intent] = Field(default=None, description="Onboarding intent: growth | tax | learning | fun")
    experience: Optional[ExperienceLevel] = Field(default=None, description="Experience level: beginner | intermediate | advanced")
    allocation_preset: Optional[AllocationPreset] = Field(default=None, description="Allocation preset: Conservative | Moderate | Aggressive | YOLO")
    risk_allocation: Optional[RiskAllocationUpdate] = None

class OnboardingUpdateResponse(BaseModel):
    user_id: int
    portfolio_size: Optional[int] = None
    intent: Optional[Intent] = None
    experience: Optional[ExperienceLevel] = None
    allocation_preset: Optional[AllocationPreset] = None
    risk_allocation: Optional[RiskAllocationUpdate] = None

    class Config:
        schema_extra = {
            "example": {
                "user_id": 1,
                "portfolio_size": 25000,
                "intent": "growth",
                "experience": "beginner",
                "allocation_preset": "Moderate",
                "risk_allocation": {
                    "collateral_pct": 40,
                    "growth_pct": 50,
                    "wildcard_pct": 10
                }
            }
        }
"""
Portfolio-related response schemas
"""

from pydantic import BaseModel, Field
from typing import List
from datetime import datetime


# --- Categorized Portfolio Schemas ---

class CategorizedAsset(BaseModel):
    symbol: str
    amount: float
    value: float
    tier: str = Field(description="Strategy tier: Collateral | Growth | Wildcard")


class TierBreakdown(BaseModel):
    tier: str
    percentage: float
    total_value: float
    assets: List[CategorizedAsset]


class CategorizedPortfolioResponse(BaseModel):
    tiers: List[TierBreakdown] = Field(description="Portfolio broken down by strategy tier")
    total_value: float
    last_updated: str
    
    class Config:
        json_schema_extra = {
            "example": {
                "tiers": [
                    {
                        "tier": "Collateral",
                        "percentage": 63.9,
                        "total_value": 6390.0,
                        "assets": [
                            {"symbol": "BTC", "amount": 0.1, "value": 4000.0, "tier": "Collateral"},
                            {"symbol": "ETH", "amount": 0.5, "value": 2390.0, "tier": "Collateral"}
                        ]
                    },
                    {
                        "tier": "Growth",
                        "percentage": 36.1,
                        "total_value": 3610.0,
                        "assets": [
                            {"symbol": "ADA", "amount": 1000, "value": 3610.0, "tier": "Growth"}
                        ]
                    },
                    {
                        "tier": "Wildcard",
                        "percentage": 0.0,
                        "total_value": 0.0,
                        "assets": []
                    }
                ],
                "total_value": 10000.0,
                "last_updated": "2025-12-13T10:30:00Z"
            }
        }


# --- Strategy Drift Schemas ---

class TierAllocation(BaseModel):
    collateral: int = Field(ge=0, le=100, description="Collateral tier percentage (0-100)")
    growth: int = Field(ge=0, le=100, description="Growth tier percentage (0-100)")
    wildcard: int = Field(ge=0, le=100, description="Wildcard tier percentage (0-100)")


class StrategyDriftResponse(BaseModel):
    target: TierAllocation = Field(description="Target tier allocations from onboarding")
    current: TierAllocation = Field(description="Current tier allocations from portfolio")
    drift: dict = Field(description="Delta per tier (current - target)")
    last_updated: datetime = Field(description="ISO timestamp of calculation")
    
    class Config:
        json_schema_extra = {
            "example": {
                "target": {
                    "collateral": 30,
                    "growth": 55,
                    "wildcard": 15
                },
                "current": {
                    "collateral": 28,
                    "growth": 62,
                    "wildcard": 10
                },
                "drift": {
                    "collateral": -2,
                    "growth": 7,
                    "wildcard": -5
                },
                "last_updated": "2025-12-13T10:30:00Z"
            }
        }


# --- AI Strategy Summary Schema ---

class StrategySummaryResponse(BaseModel):
    summary_text: str = Field(description="AI-generated portfolio summary (max 150 words)")
    generated_at: datetime = Field(description="ISO timestamp when summary was generated")
    
    class Config:
        json_schema_extra = {
            "example": {
                "summary_text": "Your portfolio aligns with a growth-focused strategy...",
                "generated_at": "2025-12-13T10:30:00Z"
            }
        }

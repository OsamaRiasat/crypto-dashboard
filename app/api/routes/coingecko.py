from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.api.services.coingecko import coingecko_service
from app.api.models.crypto import CoinData

router = APIRouter(prefix="/coingecko", tags=["coingecko"])

@router.get("/coin/{coin_id}", response_model=CoinData)
async def get_coin(coin_id: str, vs_currency: str = "usd"):
    """Get price and market data for a specific cryptocurrency from CoinGecko"""
    try:
        data = coingecko_service.get_coin_data(coin_id, vs_currency)
        if data:
            return data
        else:
            raise HTTPException(status_code=404, detail=f"Data for {coin_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/trending")
async def get_trending_coins(vs_currency: str = "usd"):
    """Get trending coins data from CoinGecko"""
    try:
        data = coingecko_service.get_trending_coins(vs_currency)
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/global")
async def get_global_data():
    """Get global cryptocurrency market data from CoinGecko"""
    try:
        data = coingecko_service.get_global_data()
        return data
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
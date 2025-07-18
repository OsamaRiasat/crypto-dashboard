from fastapi import APIRouter, HTTPException
from typing import List

from app.api.services.binance import binance_service
from app.api.models.binance import BinanceBalance, BinanceTransaction

router = APIRouter(prefix="/binance", tags=["binance"])

@router.get("/balance", response_model=List[BinanceBalance])
async def get_account_balance():
    """Get Binance account balance"""
    try:
        return binance_service.get_account_balance()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/deposits", response_model=List[BinanceTransaction])
async def get_deposit_history():
    """Get Binance deposit history"""
    try:
        return binance_service.get_deposit_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/withdrawals", response_model=List[BinanceTransaction])
async def get_withdrawal_history():
    """Get Binance withdrawal history"""
    try:
        return binance_service.get_withdrawal_history()
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
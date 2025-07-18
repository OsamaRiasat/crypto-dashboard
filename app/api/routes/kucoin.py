from fastapi import APIRouter, HTTPException, Query
from typing import Optional, List

from app.api.services.kucoin import kucoin_service
from app.api.models.crypto import KuCoinAccount, KuCoinKeyInfo

router = APIRouter(prefix="/kucoin", tags=["kucoin"])

@router.get("/accounts", response_model=List[KuCoinAccount])
async def get_accounts(currency: Optional[str] = None, account_type: Optional[str] = None):
    """Get KuCoin account information"""
    try:
        accounts = kucoin_service.get_accounts(currency, account_type)
        return accounts
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/key-info", response_model=KuCoinKeyInfo)
async def get_api_key_info():
    """Get information about the KuCoin API key"""
    try:
        key_info = kucoin_service.get_key_info()
        return key_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
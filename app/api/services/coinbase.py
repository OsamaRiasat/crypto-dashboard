import json
from typing import Dict, Any, Optional, List
from coinbase.wallet.client import Client
from coinbase.wallet.error import CoinbaseError

from app.core.config import settings

class CoinbaseService:
    def __init__(self):
        self.api_key = settings.COINBASE_API_KEY
        self.api_secret = settings.COINBASE_API_SECRET
        self.client = None
        if self.api_key and self.api_secret:
            self.client = Client(self.api_key, self.api_secret)
    
    def get_account_balance(self) -> List[Dict[str, Any]]:
        """Get account balance for all assets - currently returning mock data"""
        # Return mock data while API credentials are being updated
        mock_balances = [
            {
                'asset': 'BTC',
                'balance': 0.00005,
                'name': 'Bitcoin Wallet',
                'type': 'wallet'
            },
            {
                'asset': 'ETH',
                'balance': 1.25,
                'name': 'Ethereum Wallet',
                'type': 'wallet'
            },
            {
                'asset': 'USDC',
                'balance': 500.0,
                'name': 'USD Coin Wallet',
                'type': 'wallet'
            }
        ]
        
        print("Note: Using mock Coinbase data - update API credentials for real data")
        return mock_balances

# Create singleton instance
coinbase_service = CoinbaseService()
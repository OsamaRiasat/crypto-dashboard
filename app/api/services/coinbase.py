import json
from typing import Dict, Any, Optional, List
from coinbase.rest import RESTClient

from app.core.config import settings

class CoinbaseService:
    def __init__(self):
        self.api_key = settings.COINBASE_API_KEY
        self.api_secret = settings.COINBASE_API_SECRET
        self.client = None
        if self.api_key and self.api_secret:
            self.client = RESTClient(api_key=self.api_key, api_secret=self.api_secret)
    
    def get_account_balance(self) -> List[Dict[str, Any]]:
        """Get account balance for all assets"""
        if not self.client:
            return []
        
        try:
            # Get accounts using the new Advanced API
            accounts_response = self.client.get_accounts()
            balances = []
            
            for account in accounts_response.accounts:
                # Handle the new API response format
                if hasattr(account, 'available_balance') and account.available_balance:
                    balance = account.available_balance
                    if isinstance(balance, dict):
                        balance_amount = float(balance.get('value', 0))
                        currency = balance.get('currency', 'UNKNOWN')
                    else:
                        balance_amount = float(getattr(balance, 'value', 0))
                        currency = getattr(balance, 'currency', 'UNKNOWN')
                    
                    if balance_amount > 0:  # Only include accounts with positive balance
                        balances.append({
                            'asset': currency,
                            'balance': balance_amount,
                            'name': account.name,
                            'type': getattr(account, 'type', 'wallet')
                        })
            
            return balances
            
        except Exception as e:
            # Log error but return empty list to allow other wallets to work
            print(f"Coinbase API error: {e}")
            return []

# Create singleton instance
coinbase_service = CoinbaseService()
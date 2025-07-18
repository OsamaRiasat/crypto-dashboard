import json
from typing import Dict, Any, Optional, List
import requests
from binance.client import Client
from binance.exceptions import BinanceAPIException

from app.core.config import settings

class BinanceService:
    def __init__(self):
        self.api_key = settings.BINANCE_API_KEY
        self.api_secret = settings.BINANCE_API_SECRET
        self.client = Client(self.api_key, self.api_secret)
    
    def get_account_balance(self) -> List[Dict[str, Any]]:
        """Get account balance for all assets"""
        try:
            account = self.client.get_account()
            non_zero_balances = [
                {
                    'asset': balance['asset'],
                    'free': float(balance['free']),
                    'locked': float(balance['locked'])
                }
                for balance in account['balances']
                if float(balance['free']) > 0 or float(balance['locked']) > 0
            ]
            return non_zero_balances
        except BinanceAPIException as e:
            raise Exception(f'Error fetching account balance: {e}')
    
    def get_deposit_history(self) -> List[Dict[str, Any]]:
        """Get deposit history"""
        try:
            deposits = self.client.get_deposit_history()
            return [
                {
                    'coin': deposit['coin'],
                    'amount': float(deposit['amount']),
                    'status': deposit['status']
                }
                for deposit in deposits
            ]
        except BinanceAPIException as e:
            raise Exception(f'Error fetching deposit history: {e}')
    
    def get_withdrawal_history(self) -> List[Dict[str, Any]]:
        """Get withdrawal history"""
        try:
            withdrawals = self.client.get_withdraw_history()
            return [
                {
                    'coin': withdrawal['coin'],
                    'amount': float(withdrawal['amount']),
                    'status': withdrawal['status']
                }
                for withdrawal in withdrawals
            ]
        except BinanceAPIException as e:
            raise Exception(f'Error fetching withdrawal history: {e}')

# Create a singleton instance

binance_service = BinanceService()
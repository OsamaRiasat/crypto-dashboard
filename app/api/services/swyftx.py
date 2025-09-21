import requests
from typing import Dict, Any, Optional, List

from app.core.config import settings

class SwyftxService:
    def __init__(self):
        self.api_key = settings.SWYFTX_API_KEY
        self.access_token = settings.SWYFTX_ACCESS_TOKEN
        self.base_url = "https://api.swyftx.com.au"
        self.headers = {
            "Authorization": f"Bearer {self.access_token}",
            "X-API-KEY": self.api_key,
            "Content-Type": "application/json"
        }
    
    def get_account_balance(self) -> List[Dict[str, Any]]:
        """Get account balance for all assets"""
        try:
            # Get account balances
            response = requests.get(
                f"{self.base_url}/user/balance/",
                headers=self.headers
            )
            response.raise_for_status()
            
            balances_data = response.json()
            balances = []
            
            # Get asset info to map asset IDs to codes
            assets_response = requests.get(
                f"{self.base_url}/markets/assets/",
                headers={"X-API-KEY": self.api_key}
            )
            assets_map = {}
            if assets_response.status_code == 200:
                assets_data = assets_response.json()
                assets_map = {asset['id']: asset['code'] for asset in assets_data}
            
            for balance in balances_data:
                available_balance = float(balance.get('availableBalance', 0))
                if available_balance > 0:
                    asset_id = balance.get('assetId')
                    asset_code = assets_map.get(asset_id, balance.get('assetCode', f'ASSET_{asset_id}'))
                    
                    balances.append({
                        'asset': asset_code,
                        'balance': available_balance,
                        'name': f"{asset_code} Wallet",
                        'type': 'swyftx_wallet'
                    })
            
            return balances
            
        except Exception as e:
            print(f"Swyftx API error: {e}")
            return []
    
    def get_user_info(self) -> Dict[str, Any]:
        """Get user account information"""
        try:
            response = requests.get(
                f"{self.base_url}/user/",
                headers=self.headers
            )
            response.raise_for_status()
            return response.json()
        except Exception as e:
            print(f"Swyftx user info error: {e}")
            return {}

# Create singleton instance
swyftx_service = SwyftxService()
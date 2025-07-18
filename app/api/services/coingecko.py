import requests
import json
from typing import Dict, Any, Optional

from app.core.config import settings

class CoinGeckoService:
    def __init__(self):
        self.base_url = settings.COINGECKO_API_URL
    
    def get_coin_data(self, coin_id: str = "bitcoin", vs_currency: str = "usd") -> Optional[Dict[str, Any]]:
        """Get live price and market data for a specific cryptocurrency"""
        url = f"{self.base_url}/coins/{coin_id}"
        
        # Making a request to the CoinGecko API
        response = requests.get(url, params={"vs_currency": vs_currency})
        
        # Check if the request was successful
        if response.status_code == 200:
            data = response.json()
            
            # Extracting price and market data
            coin_data = {
                "name": data["name"],
                "symbol": data["symbol"],
                "current_price": data["market_data"]["current_price"][vs_currency],
                "market_cap": data["market_data"]["market_cap"][vs_currency],
                "volume_24h": data["market_data"]["total_volume"][vs_currency],
                "high_24h": data["market_data"]["high_24h"][vs_currency],
                "low_24h": data["market_data"]["low_24h"][vs_currency],
                "market_cap_rank": data["market_data"]["market_cap_rank"],
            }
            
            return coin_data
        else:
            raise Exception(f"Error fetching data: {response.status_code}")
    
    def get_trending_coins(self, vs_currency: str = "usd") -> Dict[str, Any]:
        """Get trending coins data"""
        url = f"{self.base_url}/search/trending"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"Error fetching trending data: {response.status_code}")
    
    def get_global_data(self) -> Dict[str, Any]:
        """Get global cryptocurrency market data"""
        url = f"{self.base_url}/global"
        
        response = requests.get(url)
        
        if response.status_code == 200:
            data = response.json()
            return data
        else:
            raise Exception(f"Error fetching global data: {response.status_code}")

# Create a singleton instance
coingecko_service = CoinGeckoService()
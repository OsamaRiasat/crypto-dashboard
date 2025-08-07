import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests

from app.api.services.kucoin import kucoin_service
from app.api.services.binance import binance_service
from app.api.services.coingecko import coingecko_service
from app.api.models.portfolio import PortfolioSummary, WalletInfo
from app.core.config import settings

class PortfolioService:
    def __init__(self):
        self.price_cache = {}
        self.cache_duration = 300  # 5 minutes cache for prices
        
    async def get_crypto_price(self, symbol: str) -> float:
        """Get current price of a cryptocurrency in USD"""
        symbol_lower = symbol.lower()
        
        # Check cache first
        current_time = datetime.now().timestamp()
        if symbol_lower in self.price_cache:
            cached_data = self.price_cache[symbol_lower]
            if current_time - cached_data['timestamp'] < self.cache_duration:
                return cached_data['price']
        
        try:
            # Map common symbols to CoinGecko IDs
            symbol_mapping = {
                'btc': 'bitcoin',
                'eth': 'ethereum',
                'usdt': 'tether',
                'usdc': 'usd-coin',
                'bnb': 'binancecoin',
                'ada': 'cardano',
                'dot': 'polkadot',
                'link': 'chainlink',
                'ltc': 'litecoin',
                'bch': 'bitcoin-cash',
                'xlm': 'stellar',
                'vet': 'vechain',
                'trx': 'tron',
                'eos': 'eos',
                'xrp': 'ripple'
            }
            
            coin_id = symbol_mapping.get(symbol_lower, symbol_lower)
            coin_data = coingecko_service.get_coin_data(coin_id, 'usd')
            
            if coin_data and 'current_price' in coin_data:
                price = float(coin_data['current_price'])
                # Cache the price
                self.price_cache[symbol_lower] = {
                    'price': price,
                    'timestamp': current_time
                }
                return price
            else:
                return 0.0
        except Exception as e:
            print(f"Error fetching price for {symbol}: {e}")
            return 0.0
    
    async def get_kucoin_portfolio(self) -> WalletInfo:
        """Get KuCoin wallet information"""
        try:
            if not all([settings.KUCOIN_API_KEY, settings.KUCOIN_API_SECRET, settings.KUCOIN_API_PASSPHRASE]):
                return WalletInfo(
                    wallet_type="kucoin",
                    connected=False,
                    total_value_usd=0.0,
                    assets=[],
                    error="API credentials not configured"
                )
            
            accounts = kucoin_service.get_accounts()
            assets = []
            total_value = 0.0
            
            for account in accounts:
                balance = float(account.get('balance', 0))
                if balance > 0:
                    currency = account.get('currency', '')
                    price = await self.get_crypto_price(currency)
                    value_usd = balance * price
                    
                    assets.append({
                        'asset': currency,
                        'balance': balance,
                        'value_usd': value_usd,
                        'account_type': account.get('type', 'trade')
                    })
                    total_value += value_usd
            
            return WalletInfo(
                wallet_type="kucoin",
                connected=True,
                total_value_usd=total_value,
                assets=assets
            )
        except Exception as e:
            return WalletInfo(
                wallet_type="kucoin",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(e)
            )
    
    async def get_binance_portfolio(self) -> WalletInfo:
        """Get Binance wallet information"""
        try:
            if not all([settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET]):
                return WalletInfo(
                    wallet_type="binance",
                    connected=False,
                    total_value_usd=0.0,
                    assets=[],
                    error="API credentials not configured"
                )
            
            balances = binance_service.get_account_balance()
            assets = []
            total_value = 0.0
            
            for balance in balances:
                total_balance = balance['free'] + balance['locked']
                if total_balance > 0:
                    asset = balance['asset']
                    price = await self.get_crypto_price(asset)
                    value_usd = total_balance * price
                    
                    assets.append({
                        'asset': asset,
                        'balance': total_balance,
                        'free': balance['free'],
                        'locked': balance['locked'],
                        'value_usd': value_usd
                    })
                    total_value += value_usd
            
            return WalletInfo(
                wallet_type="binance",
                connected=True,
                total_value_usd=total_value,
                assets=assets
            )
        except Exception as e:
            return WalletInfo(
                wallet_type="binance",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(e)
            )
    
    async def get_portfolio_summary(self) -> PortfolioSummary:
        """Get complete portfolio summary from all connected wallets"""
        # Get data from all wallets concurrently
        kucoin_task = self.get_kucoin_portfolio()
        binance_task = self.get_binance_portfolio()
        
        # Wait for all tasks to complete
        kucoin_wallet, binance_wallet = await asyncio.gather(
            kucoin_task, binance_task, return_exceptions=True
        )
        
        # Handle exceptions
        if isinstance(kucoin_wallet, Exception):
            kucoin_wallet = WalletInfo(
                wallet_type="kucoin",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(kucoin_wallet)
            )
        
        if isinstance(binance_wallet, Exception):
            binance_wallet = WalletInfo(
                wallet_type="binance",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(binance_wallet)
            )
        
        wallets = [kucoin_wallet, binance_wallet]
        
        # Calculate totals
        total_portfolio_value = sum(wallet.total_value_usd for wallet in wallets)
        connected_wallets_count = sum(1 for wallet in wallets if wallet.connected)
        
        return PortfolioSummary(
            total_portfolio_value_usd=total_portfolio_value,
            connected_wallets_count=connected_wallets_count,
            wallets=wallets,
            last_updated=datetime.utcnow().isoformat() + "Z"
        )

# Create singleton instance
portfolio_service = PortfolioService()
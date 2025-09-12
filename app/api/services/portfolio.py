import asyncio
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from decimal import Decimal, getcontext

# Set decimal precision to handle very small values
getcontext().prec = 28

from app.api.services.kucoin import kucoin_service
from app.api.services.binance import binance_service
from app.api.services.coinbase import coinbase_service
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
                'xrp': 'ripple',
                'sol': 'solana',
                'avax': 'avalanche-2',
                'matic': 'matic-network',
                'atom': 'cosmos',
                'near': 'near',
                'algo': 'algorand',
                'icp': 'internet-computer',
                'ftm': 'fantom',
                'one': 'harmony',
                'hbar': 'hedera-hashgraph',
                'flow': 'flow',
                'egld': 'elrond-erd-2',
                'theta': 'theta-token',
                'xtz': 'tezos',
                'fil': 'filecoin',
                'kcs': 'kucoin-shares',
                'arb': 'arbitrum',
                'ray': 'raydium',
                'pokt': 'pocket-network',
                'zeus': 'zeus-network'
            }
            
            coin_id = symbol_mapping.get(symbol_lower, symbol_lower)
            print(f"Fetching price for {symbol} (mapped to {coin_id})")
            
            coin_data = coingecko_service.get_coin_data(coin_id, 'usd')
            
            if coin_data and 'current_price' in coin_data:
                price = float(coin_data['current_price'])
                print(f"Successfully fetched price for {symbol}: ${price}")
                # Cache the price
                self.price_cache[symbol_lower] = {
                    'price': price,
                    'timestamp': current_time
                }
                return price
            else:
                print(f"No price data found for {symbol} (coin_id: {coin_id})")
                return 0.0
        except Exception as e:
            print(f"Error fetching price for {symbol} (coin_id: {coin_id}): {e}")
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
                balance_str = str(account.get('balance', '0'))
                balance = Decimal(balance_str)
                if balance > 0:
                    currency = account.get('currency', '')
                    price = await self.get_crypto_price(currency)
                    price_decimal = Decimal(str(price))
                    value_usd = float(balance * price_decimal)
                    
                    assets.append({
                        'asset': currency,
                        'balance': float(balance),  # Convert to float for JSON serialization
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
                free_decimal = Decimal(str(balance['free']))
                locked_decimal = Decimal(str(balance['locked']))
                total_balance = free_decimal + locked_decimal
                if total_balance > 0:
                    asset = balance['asset']
                    price = await self.get_crypto_price(asset)
                    price_decimal = Decimal(str(price))
                    value_usd = float(total_balance * price_decimal)
                    
                    assets.append({
                        'asset': asset,
                        'balance': float(total_balance),  # Convert to float for JSON serialization
                        'free': balance['free'],  # Already converted in binance service
                        'locked': balance['locked'],  # Already converted in binance service
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
    
    async def get_coinbase_portfolio(self) -> WalletInfo:
        """Get Coinbase wallet information"""
        try:
            if not all([settings.COINBASE_API_KEY, settings.COINBASE_API_SECRET]):
                return WalletInfo(
                    wallet_type="coinbase",
                    connected=False,
                    total_value_usd=0.0,
                    assets=[],
                    error="API credentials not configured"
                )
            
            balances = coinbase_service.get_account_balance()
            assets = []
            total_value = 0.0
            
            for balance in balances:
                asset = balance['asset']
                amount_decimal = Decimal(str(balance['balance']))
                price = await self.get_crypto_price(asset)
                price_decimal = Decimal(str(price))
                value_usd = float(amount_decimal * price_decimal)
                
                assets.append({
                    'asset': asset,
                    'balance': float(amount_decimal),  # Convert to float for JSON serialization
                    'value_usd': value_usd,
                    'name': balance.get('name', ''),
                    'type': balance.get('type', '')
                })
                total_value += value_usd
            
            return WalletInfo(
                wallet_type="coinbase",
                connected=True,
                total_value_usd=total_value,
                assets=assets
            )
        except Exception as e:
            return WalletInfo(
                wallet_type="coinbase",
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
        coinbase_task = self.get_coinbase_portfolio()
        
        # Wait for all tasks to complete
        kucoin_wallet, binance_wallet, coinbase_wallet = await asyncio.gather(
            kucoin_task, binance_task, coinbase_task, return_exceptions=True
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
        
        if isinstance(coinbase_wallet, Exception):
            coinbase_wallet = WalletInfo(
                wallet_type="coinbase",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(coinbase_wallet)
            )
        
        wallets = [kucoin_wallet, binance_wallet, coinbase_wallet]
        
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
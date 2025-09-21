import asyncio
import time
from datetime import datetime
from typing import Dict, Any, List, Optional
import requests
from decimal import Decimal, getcontext

# Set high precision for decimal calculations
getcontext().prec = 28

from app.api.services.kucoin import kucoin_service
from app.api.services.binance import binance_service
from app.api.services.coinbase import coinbase_service
from app.api.services.swyftx import swyftx_service
from app.api.services.coingecko import coingecko_service
from app.api.models.portfolio import PortfolioSummary, WalletInfo
from app.core.config import settings

class PortfolioService:
    def __init__(self):
        self.price_cache = {}
        self.cache_duration = 300  # 5 minutes cache for prices
        self.rate_limit_cache = {}  # Track rate limit failures
        self.popular_coins_cache_duration = 900  # 15 minutes for popular coins (BTC, ETH, etc.)
        
    async def get_crypto_price(self, symbol: str) -> float:
        """Get current price of a cryptocurrency in USD"""
        symbol_lower = symbol.lower()
        
        # Check cache first with different durations for popular coins
        current_time = datetime.now().timestamp()
        popular_coins = ['btc', 'eth', 'usdt', 'usdc', 'bnb']
        cache_duration = self.popular_coins_cache_duration if symbol_lower in popular_coins else self.cache_duration
        
        if symbol_lower in self.price_cache:
            cached_data = self.price_cache[symbol_lower]
            if current_time - cached_data['timestamp'] < cache_duration:
                return cached_data['price']
        
        # Check if we recently hit rate limit for this symbol
        if symbol_lower in self.rate_limit_cache:
            last_rate_limit = self.rate_limit_cache[symbol_lower]
            if current_time - last_rate_limit < 60:  # Wait 1 minute after rate limit
                print(f"Skipping {symbol} due to recent rate limit (waiting 60s)")
                return self.price_cache.get(symbol_lower, {}).get('price', 0.0)
        
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
                'zeus': 'zeus-network',
                'gtc': 'gitcoin',
                'shib': 'shiba-inu',
                'omg': 'omg-network',
                'aud': 'audius',
                'audio': 'audius'
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
            error_msg = str(e)
            print(f"Error fetching price for {symbol} (coin_id: {coin_id}): {e}")
            
            # Track rate limit errors
            if "429" in error_msg or "rate limit" in error_msg.lower():
                self.rate_limit_cache[symbol_lower] = current_time
                print(f"Rate limit detected for {symbol}, caching failure for 60s")
                # Return cached price if available
                if symbol_lower in self.price_cache:
                    cached_price = self.price_cache[symbol_lower]['price']
                    print(f"Returning cached price for {symbol}: ${cached_price}")
                    return cached_price
            
            return 0.0
    
    async def get_batch_crypto_prices(self, symbols: set) -> Dict[str, float]:
        """Get prices for multiple cryptocurrencies in a single batch call"""
        if not symbols:
            return {}
        
        current_time = datetime.now().timestamp()
        prices = {}
        symbols_to_fetch = set()
        
        # Symbol mapping (same as in get_crypto_price)
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
            'zeus': 'zeus-network',
            'gtc': 'gitcoin',
            'shib': 'shiba-inu',
            'omg': 'omg-network',
            'aud': 'audius',
            'audio': 'audius'
        }
        
        # Check cache and collect symbols that need fetching
        for symbol in symbols:
            symbol_lower = symbol.lower()
            popular_coins = ['btc', 'eth', 'usdt', 'usdc', 'bnb']
            cache_duration = self.popular_coins_cache_duration if symbol_lower in popular_coins else self.cache_duration
            
            # Check cache first
            if symbol_lower in self.price_cache:
                cached_data = self.price_cache[symbol_lower]
                if current_time - cached_data['timestamp'] < cache_duration:
                    prices[symbol] = cached_data['price']
                    continue
            
            # Check rate limit
            if symbol_lower in self.rate_limit_cache:
                last_rate_limit = self.rate_limit_cache[symbol_lower]
                if current_time - last_rate_limit < 60:
                    prices[symbol] = self.price_cache.get(symbol_lower, {}).get('price', 0.0)
                    continue
            
            symbols_to_fetch.add(symbol)
        
        # Fetch prices for symbols not in cache
        if symbols_to_fetch:
            try:
                # Map symbols to CoinGecko IDs
                coin_ids = []
                symbol_to_coin_id = {}
                for symbol in symbols_to_fetch:
                    symbol_lower = symbol.lower()
                    coin_id = symbol_mapping.get(symbol_lower, symbol_lower)
                    coin_ids.append(coin_id)
                    symbol_to_coin_id[symbol] = coin_id
                
                print(f"Fetching batch prices for {len(coin_ids)} coins: {coin_ids}")
                
                # Get batch prices from CoinGecko
                batch_prices = coingecko_service.get_multiple_coin_prices(coin_ids, 'usd')
                
                # Map results back to original symbols and cache them
                for symbol in symbols_to_fetch:
                    coin_id = symbol_to_coin_id[symbol]
                    if coin_id in batch_prices:
                        price = batch_prices[coin_id]
                        prices[symbol] = price
                        # Cache the price
                        self.price_cache[symbol.lower()] = {
                            'price': price,
                            'timestamp': current_time
                        }
                        print(f"Successfully fetched price for {symbol}: ${price}")
                    else:
                        print(f"No price data found for {symbol} (coin_id: {coin_id})")
                        prices[symbol] = 0.0
                        
            except Exception as e:
                error_msg = str(e)
                print(f"Error fetching batch prices: {e}")
                
                # Handle rate limit for all symbols
                if "429" in error_msg or "rate limit" in error_msg.lower():
                    for symbol in symbols_to_fetch:
                        symbol_lower = symbol.lower()
                        self.rate_limit_cache[symbol_lower] = current_time
                        # Return cached price if available
                        prices[symbol] = self.price_cache.get(symbol_lower, {}).get('price', 0.0)
                else:
                    # For other errors, set price to 0
                    for symbol in symbols_to_fetch:
                        prices[symbol] = 0.0
        
        return prices
    
    async def get_kucoin_portfolio_with_prices(self, batch_prices: Dict[str, float]) -> WalletInfo:
        """Get KuCoin wallet information using pre-fetched prices"""
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
                    price = batch_prices.get(currency, 0.0)
                    price_decimal = Decimal(str(price))
                    value_usd = float(balance * price_decimal)
                    
                    assets.append({
                        'asset': currency,
                        'balance': float(balance),
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
    
    async def get_binance_portfolio_with_prices(self, batch_prices: Dict[str, float]) -> WalletInfo:
        """Get Binance wallet information using pre-fetched prices"""
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
                free_balance = Decimal(str(balance.get('free', 0)))
                locked_balance = Decimal(str(balance.get('locked', 0)))
                total_balance = free_balance + locked_balance
                
                if total_balance > 0:
                    asset = balance.get('asset', '')
                    price = batch_prices.get(asset, 0.0)
                    price_decimal = Decimal(str(price))
                    value_usd = float(total_balance * price_decimal)
                    
                    assets.append({
                        'asset': asset,
                        'balance': float(total_balance),
                        'free': float(free_balance),
                        'locked': float(locked_balance),
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
    
    async def get_coinbase_portfolio_with_prices(self, batch_prices: Dict[str, float]) -> WalletInfo:
        """Get Coinbase wallet information using pre-fetched prices"""
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
                amount = Decimal(str(balance.get('balance', 0)))
                
                if amount > 0:
                    currency = balance.get('asset', '')
                    price = batch_prices.get(currency, 0.0)
                    price_decimal = Decimal(str(price))
                    value_usd = float(amount * price_decimal)
                    
                    assets.append({
                        'asset': currency,
                        'balance': float(amount),
                        'value_usd': value_usd,
                        'account_name': balance.get('name', ''),
                        'account_type': balance.get('type', '')
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

    async def get_swyftx_portfolio_with_prices(self, batch_prices: Dict[str, float]) -> WalletInfo:
        """Get Swyftx wallet information using pre-fetched prices"""
        try:
            if not all([settings.SWYFTX_API_KEY, settings.SWYFTX_ACCESS_TOKEN]):
                return WalletInfo(
                    wallet_type="swyftx",
                    connected=False,
                    total_value_usd=0.0,
                    assets=[],
                    error="API credentials not configured"
                )
            
            balances = swyftx_service.get_account_balance()
            assets = []
            total_value = 0.0
            
            for balance in balances:
                available_balance = Decimal(str(balance.get('balance', 0)))
                
                if available_balance > 0:
                    asset_code = balance.get('asset', '')
                    price = batch_prices.get(asset_code, 0.0)
                    price_decimal = Decimal(str(price))
                    value_usd = float(available_balance * price_decimal)
                    
                    assets.append({
                        'asset': asset_code,
                        'balance': float(available_balance),
                        'value_usd': value_usd
                    })
                    total_value += value_usd
            
            return WalletInfo(
                wallet_type="swyftx",
                connected=True,
                total_value_usd=total_value,
                assets=assets
            )
        except Exception as e:
            return WalletInfo(
                wallet_type="swyftx",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(e)
            )
    
    async def get_swyftx_portfolio(self) -> WalletInfo:
        """Get Swyftx wallet information"""
        try:
            balances = swyftx_service.get_account_balance()
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
                    'balance': float(amount_decimal),
                    'value_usd': value_usd,
                    'name': balance.get('name', ''),
                    'type': balance.get('type', '')
                })
                total_value += value_usd
            
            return WalletInfo(
                wallet_type="swyftx",
                connected=True,
                total_value_usd=total_value,
                assets=assets
            )
        except Exception as e:
            return WalletInfo(
                wallet_type="swyftx",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(e)
            )

    async def get_portfolio_summary(self) -> PortfolioSummary:
        """Get complete portfolio summary from all connected wallets"""
        # First, collect all unique assets from all wallets
        all_assets = set()
        
        # Get raw balance data from all services
        try:
            if all([settings.KUCOIN_API_KEY, settings.KUCOIN_API_SECRET, settings.KUCOIN_API_PASSPHRASE]):
                kucoin_accounts = kucoin_service.get_accounts()
                for account in kucoin_accounts:
                    if Decimal(str(account.get('balance', '0'))) > 0:
                        all_assets.add(account.get('currency', ''))
        except Exception:
            pass
        
        try:
            if all([settings.BINANCE_API_KEY, settings.BINANCE_API_SECRET]):
                binance_balances = binance_service.get_account_balance()
                for balance in binance_balances:
                    free_decimal = Decimal(str(balance['free']))
                    locked_decimal = Decimal(str(balance['locked']))
                    if (free_decimal + locked_decimal) > 0:
                        all_assets.add(balance['asset'])
        except Exception:
            pass
        
        try:
            if all([settings.COINBASE_API_KEY, settings.COINBASE_API_SECRET]):
                coinbase_balances = coinbase_service.get_account_balance()
                for balance in coinbase_balances:
                    all_assets.add(balance['asset'])
        except Exception:
            pass
        
        try:
            if all([settings.SWYFTX_API_KEY, settings.SWYFTX_ACCESS_TOKEN]):
                swyftx_balances = swyftx_service.get_account_balance()
                for balance in swyftx_balances:
                    all_assets.add(balance['asset'])
        except Exception:
            pass
        
        # Remove empty strings and None values
        all_assets = {asset for asset in all_assets if asset}
        
        # Fetch all prices in a single batch call
        batch_prices = await self.get_batch_crypto_prices(all_assets)
        
        # Get data from all wallets concurrently with pre-fetched prices
        kucoin_task = self.get_kucoin_portfolio_with_prices(batch_prices)
        binance_task = self.get_binance_portfolio_with_prices(batch_prices)
        coinbase_task = self.get_coinbase_portfolio_with_prices(batch_prices)
        swyftx_task = self.get_swyftx_portfolio_with_prices(batch_prices)
        
        # Wait for all tasks to complete
        kucoin_wallet, binance_wallet, coinbase_wallet, swyftx_wallet = await asyncio.gather(
            kucoin_task, binance_task, coinbase_task, swyftx_task, return_exceptions=True
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
        
        if isinstance(swyftx_wallet, Exception):
            swyftx_wallet = WalletInfo(
                wallet_type="swyftx",
                connected=False,
                total_value_usd=0.0,
                assets=[],
                error=str(swyftx_wallet)
            )
        
        wallets = [kucoin_wallet, binance_wallet, coinbase_wallet, swyftx_wallet]
        
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
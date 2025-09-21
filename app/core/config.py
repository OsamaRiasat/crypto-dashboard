import os
from pydantic_settings import BaseSettings
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings(BaseSettings):
    # API information
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "Crypto Dashboard API"
    PROJECT_DESCRIPTION: str = "API for CoinGecko, KuCoin, and Binance data"
    VERSION: str = "1.0.0"
    
    # CORS configuration
    BACKEND_CORS_ORIGINS: list = ["*"]
    
    # KuCoin API credentials
    KUCOIN_API_KEY: str = os.getenv("KUCOIN_API_KEY", "")
    KUCOIN_API_SECRET: str = os.getenv("KUCOIN_API_SECRET", "")
    KUCOIN_API_PASSPHRASE: str = os.getenv("KUCOIN_API_PASSPHRASE", "")
    
    # Binance API credentials
    BINANCE_API_KEY: str = os.getenv("BINANCE_API_KEY", "")
    BINANCE_API_SECRET: str = os.getenv("BINANCE_API_SECRET", "")
    
    # Coinbase API credentials
    COINBASE_API_KEY: str = os.getenv("COINBASE_API_KEY", "")
    COINBASE_API_SECRET: str = os.getenv("COINBASE_API_SECRET", "")
    
    # Swyftx API credentials
    SWYFTX_API_KEY: str = os.getenv("SWYFTX_API_KEY", "")
    SWYFTX_ACCESS_TOKEN: str = os.getenv("SWYFTX_ACCESS_TOKEN", "")
    
    # API endpoints
    COINGECKO_API_URL: str = "https://api.coingecko.com/api/v3"
    KUCOIN_API_URL: str = "https://api.kucoin.com"
    
    class Config:
        case_sensitive = True

# Create settings instance
settings = Settings()
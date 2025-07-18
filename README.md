# Crypto Dashboard API

This project provides a FastAPI backend that exposes APIs for CoinGecko, KuCoin, and Binance cryptocurrency data.

## Features

- Real-time cryptocurrency price and market data from CoinGecko
- Account information and trading data from KuCoin
- Account balances and transaction history from Binance

## Project Structure

```
├── app/                    # Main application package
│   ├── api/                # API related modules
│   │   ├── models/         # Pydantic models for request/response
│   │   ├── routes/         # API route definitions
│   │   └── services/       # Service layer for business logic
│   ├── core/               # Core application modules
│   │   └── config.py       # Application configuration
│   ├── utils/              # Utility functions and helpers
│   └── main.py             # FastAPI application instance
├── .env                    # Environment variables
├── requirements.txt        # Project dependencies
└── run.py                  # Application entry point
```

## Environment Variables

Create a `.env` file in the root directory with the following variables:

```env
# KuCoin API Credentials
KUCOIN_API_KEY=your_kucoin_api_key
KUCOIN_API_SECRET=your_kucoin_api_secret
KUCOIN_API_PASSPHRASE=your_kucoin_api_passphrase

# Binance API Credentials
BINANCE_API_KEY=your_binance_api_key
BINANCE_API_SECRET=your_binance_api_secret
```

## Running the API

Start the FastAPI server:

```bash
python run.py
```

Alternatively, you can use uvicorn directly:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

The API will be available at http://localhost:8000

## API Endpoints

### CoinGecko
- GET `/api/v1/coingecko/coin/{coin_id}` - Get price and market data for a specific cryptocurrency
- GET `/api/v1/coingecko/trending` - Get trending coins
- GET `/api/v1/coingecko/global` - Get global cryptocurrency market data

### KuCoin
- GET `/api/v1/kucoin/accounts` - Get account information
- GET `/api/v1/kucoin/key-info` - Get API key information

### Binance
- GET `/api/v1/binance/balance` - Get account balances
- GET `/api/v1/binance/deposits` - Get deposit history
- GET `/api/v1/binance/withdrawals` - Get withdrawal history
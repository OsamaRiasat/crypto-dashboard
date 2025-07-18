import os
import requests
import json
import time
import base64
import hmac
import hashlib
from urllib.parse import urlencode
from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Crypto Dashboard API", description="API for CoinGecko and KuCoin data")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Import CoinGecko functionality
from coingecko import get_coin_data

# KuCoin API credentials
api_key = os.getenv("KUCOIN_API_KEY")
api_secret = os.getenv("KUCOIN_API_SECRET")
api_passphrase = os.getenv("KUCOIN_API_PASSPHRASE")

# KuCoin Signer class
class KcSigner:
    def __init__(self, api_key: str, api_secret: str, api_passphrase: str):
        self.api_key = api_key or ""
        self.api_secret = api_secret or ""
        self.api_passphrase = api_passphrase or ""

        if api_passphrase and api_secret:
            self.api_passphrase = self.sign(api_passphrase.encode('utf-8'), api_secret.encode('utf-8'))

    def sign(self, plain: bytes, key: bytes) -> str:
        hm = hmac.new(key, plain, hashlib.sha256)
        return base64.b64encode(hm.digest()).decode()

    def headers(self, plain: str) -> dict:
        timestamp = str(int(time.time() * 1000))
        signature = self.sign((timestamp + plain).encode('utf-8'), self.api_secret.encode('utf-8'))

        return {
            "KC-API-KEY": self.api_key,
            "KC-API-PASSPHRASE": self.api_passphrase,
            "KC-API-TIMESTAMP": timestamp,
            "KC-API-SIGN": signature,
            "KC-API-KEY-VERSION": "2"
        }

# Helper function for KuCoin API requests
def process_headers(signer: KcSigner, body: bytes, raw_url: str, request: requests.PreparedRequest, method: str):
    request.headers["Content-Type"] = "application/json"
    payload = method + raw_url + body.decode()
    headers = signer.headers(payload)
    request.headers.update(headers)

# Create KuCoin signer instance
kucoin_signer = KcSigner(api_key, api_secret, api_passphrase)

# API Routes

# CoinGecko Routes
@app.get("/api/coingecko/coin/{coin_id}")
async def get_coin(coin_id: str, vs_currency: str = "usd"):
    """Get price and market data for a specific cryptocurrency from CoinGecko"""
    try:
        data = get_coin_data(coin_id, vs_currency)
        if data:
            return data
        else:
            raise HTTPException(status_code=404, detail=f"Data for {coin_id} not found")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# KuCoin Routes
@app.get("/api/kucoin/accounts")
async def get_accounts(currency: Optional[str] = None, account_type: Optional[str] = None):
    """Get KuCoin account information"""
    try:
        endpoint = "https://api.kucoin.com"
        path = "/api/v1/accounts"
        method = "GET"
        
        # Prepare query parameters
        query_params = {}
        if currency:
            query_params["currency"] = currency
        if account_type:
            query_params["type"] = account_type
        
        # Build URL with query parameters
        query_string = urlencode(query_params) if query_params else ""
        raw_url = f"{path}?{query_string}" if query_string else path
        full_path = f"{endpoint}{raw_url}"
        
        # Prepare and send the request
        session = requests.Session()
        req = requests.Request(method=method, url=full_path).prepare()
        process_headers(kucoin_signer, b"", raw_url, req, method)
        
        resp = session.send(req)
        resp.raise_for_status()
        resp_obj = json.loads(resp.content)
        
        # Check if the request was successful
        if resp_obj.get('code') == '200000':
            return resp_obj.get('data', [])
        else:
            raise HTTPException(status_code=400, detail=f"API Error: {resp_obj}")
    except requests.exceptions.HTTPError as e:
        raise HTTPException(status_code=500, detail=f"HTTP Error: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error: {str(e)}")

@app.get("/api/kucoin/key-info")
async def get_api_key_info():
    """Get information about the KuCoin API key"""
    try:
        endpoint = "https://api.kucoin.com"
        path = "/api/v1/user/api-key"
        method = "GET"
        
        # Build full URL
        full_path = f"{endpoint}{path}"
        
        # Prepare and send the request
        session = requests.Session()
        req = requests.Request(method=method, url=full_path).prepare()
        process_headers(kucoin_signer, b"", path, req, method)
        
        resp = session.send(req)
        resp.raise_for_status()
        resp_obj = json.loads(resp.content)
        
        # Check if the request was successful
        if resp_obj.get('code') == '200000':
            return resp_obj.get('data', {})
        else:
            raise HTTPException(status_code=400, detail=f"API Error: {resp_obj}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# Health check endpoint
@app.get("/health")
async def health_check():
    return {"status": "healthy"}

# Root endpoint
@app.get("/")
async def root():
    return {"message": "Welcome to the Crypto Dashboard API"}

# Run the application
if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api:app", host="0.0.0.0", port=8000, reload=True)
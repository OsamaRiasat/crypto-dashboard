import base64
import hashlib
import hmac
import json
import time
from urllib.parse import urlencode
import requests
from typing import Optional, Dict, Any, List

from app.core.config import settings

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

class KuCoinService:
    def __init__(self):
        self.api_key = settings.KUCOIN_API_KEY
        self.api_secret = settings.KUCOIN_API_SECRET
        self.api_passphrase = settings.KUCOIN_API_PASSPHRASE
        self.base_url = settings.KUCOIN_API_URL
        self.signer = KcSigner(self.api_key, self.api_secret, self.api_passphrase)
        self.session = requests.Session()
    
    def _process_headers(self, body: bytes, raw_url: str, request: requests.PreparedRequest, method: str):
        request.headers["Content-Type"] = "application/json"
        payload = method + raw_url + body.decode()
        headers = self.signer.headers(payload)
        request.headers.update(headers)
    
    def get_accounts(self, currency: Optional[str] = None, account_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Get all accounts or filter by currency and account type"""
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
        full_path = f"{self.base_url}{raw_url}"
        
        # Prepare and send the request
        req = requests.Request(method=method, url=full_path).prepare()
        self._process_headers(b"", raw_url, req, method)
        
        resp = self.session.send(req)
        resp.raise_for_status()
        resp_obj = json.loads(resp.content)
        
        # Check if the request was successful
        if resp_obj.get('code') == '200000':
            return resp_obj.get('data', [])
        else:
            raise Exception(f"API Error: {resp_obj}")
    
    def get_key_info(self) -> Dict[str, Any]:
        """Get information about the KuCoin API key"""
        path = "/api/v1/user/api-key"
        method = "GET"
        
        # Build full URL
        full_path = f"{self.base_url}{path}"
        
        # Prepare and send the request
        req = requests.Request(method=method, url=full_path).prepare()
        self._process_headers(b"", path, req, method)
        
        resp = self.session.send(req)
        resp.raise_for_status()
        resp_obj = json.loads(resp.content)
        
        # Check if the request was successful
        if resp_obj.get('code') == '200000':
            return resp_obj.get('data', {})
        else:
            raise Exception(f"API Error: {resp_obj}")

# Create a singleton instance
kucoin_service = KuCoinService()
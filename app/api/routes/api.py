from fastapi import APIRouter

from app.api.routes import coingecko, kucoin, binance, portfolio, chatbot, auth
from app.core.config import settings

# Create the main API router
api_router = APIRouter(prefix=settings.API_V1_STR)

# Include all route modules
api_router.include_router(coingecko.router)
api_router.include_router(kucoin.router)
api_router.include_router(binance.router)
api_router.include_router(portfolio.router)
api_router.include_router(chatbot.router)
api_router.include_router(auth.router)
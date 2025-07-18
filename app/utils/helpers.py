import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

def get_logger(name: str) -> logging.Logger:
    """Get a logger with the given name"""
    return logging.getLogger(name)

def format_response(data: Any, message: Optional[str] = None, success: bool = True) -> Dict[str, Any]:
    """Format a standard API response"""
    return {
        "success": success,
        "message": message,
        "data": data
    }
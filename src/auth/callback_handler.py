"""
Callback handler for implicit OAuth flow (response_type=token).
Handles token extraction from URL fragment.
"""
import re
from typing import Optional, Dict, Any
from urllib.parse import urlparse, parse_qs

try:
    from ..utils.logger import logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from utils.logger import logger


def extract_token_from_fragment(url: str) -> Optional[Dict[str, Any]]:
    """
    Extract access token from URL fragment (implicit OAuth flow).
    
    Format: http://localhost:8000/callback#access_token=TOKEN&expires_in=3600&token_type=bearer
    
    Args:
        url: Full callback URL with fragment
        
    Returns:
        Dict with access_token, expires_in, token_type, or None if not found
    """
    try:
        parsed = urlparse(url)
        fragment = parsed.fragment
        
        if not fragment:
            return None
        
        # Parse fragment (format: key=value&key2=value2)
        params = {}
        for param in fragment.split('&'):
            if '=' in param:
                key, value = param.split('=', 1)
                params[key] = value
        
        # Check for access token
        if 'access_token' in params:
            result = {
                'access_token': params['access_token'],
                'expires_in': int(params.get('expires_in', 0)),
                'token_type': params.get('token_type', 'bearer')
            }
            
            # Extract error if present
            if 'error' in params:
                result['error'] = params['error']
                result['error_reason'] = params.get('error_reason')
                result['error_description'] = params.get('error_description')
            
            logger.info(f"Extracted token from fragment (expires in {result['expires_in']}s)")
            return result
        
        return None
    except Exception as e:
        logger.error(f"Failed to extract token from fragment: {e}")
        return None


def extract_code_from_query(url: str) -> Optional[str]:
    """
    Extract authorization code from URL query (authorization code flow).
    
    Format: http://localhost:8000/callback?code=CODE&state=STATE
    
    Args:
        url: Full callback URL with query params
        
    Returns:
        Authorization code or None if not found
    """
    try:
        parsed = urlparse(url)
        params = parse_qs(parsed.query)
        code = params.get('code', [None])[0]
        return code
    except Exception as e:
        logger.error(f"Failed to extract code from query: {e}")
        return None


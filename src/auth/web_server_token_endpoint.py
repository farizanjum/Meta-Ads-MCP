"""
Token endpoint for handling implicit OAuth flow tokens.
This endpoint receives tokens POSTed from the callback page JavaScript.
"""
from fastapi import APIRouter, HTTPException, Request
from pydantic import BaseModel
from typing import Optional

try:
    from ..config.settings import settings
    from ..utils.logger import logger
    from .oauth_service import oauth_service
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config.settings import settings
    from utils.logger import logger
    from oauth_service import oauth_service

router = APIRouter()


class TokenRequest(BaseModel):
    access_token: str
    expires_in: Optional[int] = 0
    token_type: Optional[str] = "bearer"
    state: Optional[str] = None


@router.post("/auth/facebook/callback/token")
async def process_token(request: Request, token_data: TokenRequest):
    """
    Process token from implicit OAuth flow.
    Called by callback.html JavaScript after extracting token from URL fragment.
    """
    try:
        logger.info("Processing token from implicit OAuth flow")
        
        if not token_data.access_token:
            raise HTTPException(status_code=400, detail="Missing access_token")
        
        # Get user info
        logger.info("Fetching user info from Facebook")
        user_info = oauth_service.get_user_info(token_data.access_token)
        if not user_info or not user_info.get("id"):
            raise HTTPException(status_code=400, detail="Failed to get user info from Facebook")
        
        fb_user_id = user_info.get("id")
        logger.info(f"Got FB user ID: {fb_user_id}")
        
        # Exchange short token for long (if we have app secret)
        try:
            logger.info("Exchanging short token for long-lived token")
            long_token_response = oauth_service.exchange_short_token_for_long(token_data.access_token)
            long_token = long_token_response.get("access_token")
            expires_in = long_token_response.get("expires_in", 5184000)
            logger.info(f"Got long-lived token, expires in {expires_in} seconds")
        except Exception as e:
            logger.warning(f"Could not exchange for long token: {e}, using short token")
            # If exchange fails, use the token as-is
            long_token = token_data.access_token
            expires_in = token_data.expires_in or 3600
        
        # Get ad accounts
        accounts = []
        try:
            logger.info("Fetching ad accounts")
            accounts = oauth_service.get_ad_accounts(long_token)
            logger.info(f"Found {len(accounts)} ad accounts")
        except Exception as e:
            logger.warning(f"Could not fetch ad accounts: {e}")
        
        # Save token
        logger.info(f"Saving token to database for FB user {fb_user_id}")
        permissions = settings.fb_oauth_scopes.split(",") if settings.fb_oauth_scopes else []
        try:
            token_record = oauth_service.save_token(
                user_id=None,
                fb_user_id=fb_user_id,
                access_token=long_token,
                expires_in=expires_in,
                permissions=permissions,
                accounts=accounts
            )
            # Access the ID safely by catching any potential detached instance error
            try:
                record_id = token_record.id if hasattr(token_record, 'id') else 'unknown'
                logger.info(f"Successfully saved token for user {fb_user_id}, token record ID: {record_id}")
            except Exception:
                logger.info(f"Successfully saved token for user {fb_user_id}")
            
            # Verify token was saved by trying to retrieve it
            verify_token = oauth_service.get_token(fb_user_id=fb_user_id)
            if verify_token:
                logger.info("Token verification successful - token can be retrieved")
            else:
                logger.error("WARNING: Token was saved but could not be retrieved!")
        except Exception as e:
            logger.error(f"Failed to save token: {e}", exc_info=True)
            raise HTTPException(status_code=500, detail=f"Failed to save token: {str(e)}")
        
        return {"status": "success", "message": "Token processed and saved successfully", "fb_user_id": fb_user_id}
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error processing token: {e}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


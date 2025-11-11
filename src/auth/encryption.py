"""
Token encryption utilities for secure storage.
Supports local symmetric encryption and KMS integration (future).
"""
import base64
import os
from typing import Optional
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

try:
    from ..config.settings import settings
    from ..utils.logger import logger
except ImportError:
    import sys
    import os
    sys.path.insert(0, os.path.dirname(__file__))
    from config.settings import settings
    from utils.logger import logger


class TokenEncryption:
    """
    Handles encryption and decryption of access tokens.
    
    Uses Fernet (symmetric encryption) with a key derived from:
    - KMS key (production) or
    - Local key material (development)
    """
    
    def __init__(self, encryption_key: Optional[str] = None):
        """
        Initialize encryption with key.
        
        Args:
            encryption_key: KMS key reference or local key material
        """
        self.encryption_key = encryption_key or settings.token_encryption_key
        self._fernet: Optional[Fernet] = None
        self._initialize_fernet()
    
    def _initialize_fernet(self) -> None:
        """Initialize Fernet cipher with derived key."""
        try:
            # If key is a KMS reference, fetch from KMS (future implementation)
            # For now, treat as local key material
            key_material = self.encryption_key.encode()
            
            # Derive a 32-byte key using PBKDF2
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=b'meta_ads_oauth_salt',  # In production, use random salt per key
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(key_material))
            self._fernet = Fernet(key)
        except Exception as e:
            logger.error(f"Failed to initialize encryption: {e}")
            raise
    
    def encrypt(self, token: str) -> str:
        """
        Encrypt a token.
        
        Args:
            token: Plaintext token to encrypt
            
        Returns:
            Base64-encoded encrypted token
        """
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")
        
        try:
            encrypted = self._fernet.encrypt(token.encode())
            return base64.urlsafe_b64encode(encrypted).decode()
        except Exception as e:
            logger.error(f"Token encryption failed: {e}")
            raise
    
    def decrypt(self, encrypted_token: str) -> str:
        """
        Decrypt a token.
        
        Args:
            encrypted_token: Base64-encoded encrypted token
            
        Returns:
            Plaintext token
        """
        if not self._fernet:
            raise RuntimeError("Encryption not initialized")
        
        try:
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_token.encode())
            decrypted = self._fernet.decrypt(encrypted_bytes)
            return decrypted.decode()
        except Exception as e:
            logger.error(f"Token decryption failed: {e}")
            raise


# Global encryption instance
_encryption_instance: Optional[TokenEncryption] = None


def get_encryption() -> TokenEncryption:
    """Get or create global encryption instance."""
    global _encryption_instance
    if _encryption_instance is None:
        _encryption_instance = TokenEncryption()
    return _encryption_instance


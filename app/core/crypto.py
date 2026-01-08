"""
Cryptographic utilities for secure PIN handling and data protection.
Uses bcrypt for password hashing with automatic salt generation.
"""

from passlib.context import CryptContext
from typing import Optional
import secrets

# Configure password hashing context with bcrypt
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def hash_pin(pin: str) -> str:
    """
    Hash a PIN using bcrypt with automatic salt generation.
    
    Args:
        pin: Plain text PIN (should be 4 digits)
        
    Returns:
        Hashed PIN string suitable for database storage
        
    Example:
        >>> hashed = hash_pin("1234")
        >>> print(len(hashed))  # Will be ~60 characters
        60
    """
    if not pin or not pin.isdigit():
        raise ValueError("PIN must contain only digits")
    
    if len(pin) != 4:
        raise ValueError("PIN must be exactly 4 digits")
    
    return pwd_context.hash(pin)


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """
    Verify a plain text PIN against a hashed PIN.
    Uses constant-time comparison to prevent timing attacks.
    
    Args:
        plain_pin: Plain text PIN to verify
        hashed_pin: Hashed PIN from database
        
    Returns:
        True if PIN matches, False otherwise
        
    Example:
        >>> hashed = hash_pin("1234")
        >>> verify_pin("1234", hashed)
        True
        >>> verify_pin("5678", hashed)
        False
    """
    if not plain_pin or not hashed_pin:
        return False
    
    try:
        return pwd_context.verify(plain_pin, hashed_pin)
    except Exception:
        # Handle any verification errors (malformed hash, etc.)
        return False


def generate_secure_token(length: int = 32) -> str:
    """
    Generate a cryptographically secure random token.
    Useful for session tokens, API keys, etc.
    
    Args:
        length: Length of the token in bytes (default 32)
        
    Returns:
        Hex-encoded random token
        
    Example:
        >>> token = generate_secure_token()
        >>> len(token)
        64  # 32 bytes = 64 hex characters
    """
    return secrets.token_hex(length)


def needs_rehash(hashed_pin: str) -> bool:
    """
    Check if a hashed PIN needs to be rehashed.
    This is useful when upgrading hashing algorithms or parameters.
    
    Args:
        hashed_pin: Hashed PIN from database
        
    Returns:
        True if PIN should be rehashed, False otherwise
    """
    return pwd_context.needs_update(hashed_pin)

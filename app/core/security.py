import bcrypt


def hash_pin(pin: str) -> str:
    """
    Hash a PIN using bcrypt.
    
    Args:
        pin: Plain text PIN (4 digits)
        
    Returns:
        Bcrypt hashed PIN as a string
    """
    # Convert PIN to bytes and hash it
    pin_bytes = pin.encode('utf-8')
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(pin_bytes, salt)
    # Return as string for storage in database
    return hashed.decode('utf-8')


def verify_pin(plain_pin: str, hashed_pin: str) -> bool:
    """
    Verify a plain PIN against a bcrypt hash.
    
    Args:
        plain_pin: Plain text PIN to verify
        hashed_pin: Bcrypt hashed PIN from database
        
    Returns:
        True if PIN matches, False otherwise
    """
    try:
        plain_bytes = plain_pin.encode('utf-8')
        hashed_bytes = hashed_pin.encode('utf-8')
        return bcrypt.checkpw(plain_bytes, hashed_bytes)
    except Exception:
        # If any error occurs during verification, return False
        return False

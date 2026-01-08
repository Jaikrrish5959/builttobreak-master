from sqlalchemy.orm import Session
from app.database.models import Wallet
from app.schemas.wallet import WalletCreate
from fastapi import HTTPException
from app.core.crypto import hash_pin, verify_pin

def create_wallet(db: Session, wallet: WalletCreate):
    # Hash the PIN before storing
    hashed_pin = hash_pin(wallet.pin)
    db_wallet = Wallet(user_id=wallet.user_id, pin_hash=hashed_pin)
    db.add(db_wallet)
    db.commit()
    db.refresh(db_wallet)
    return db_wallet

def get_wallet(db: Session, wallet_id: int):
    return db.query(Wallet).filter(Wallet.id == wallet_id).first()

def get_wallets(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Wallet).offset(skip).limit(limit).all()

def verify_wallet_pin(db: Session, wallet_id: int, pin: str) -> bool:
    """Verify if the provided PIN matches the wallet's hashed PIN"""
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        return False
    return verify_pin(pin, wallet.pin_hash)

def deposit_wallet(db: Session, wallet_id: int, amount: float, pin: str):
    wallet = get_wallet(db, wallet_id)
    if not wallet:
        return None
    
    # Verify PIN using secure comparison
    if not verify_pin(pin, wallet.pin_hash):
        raise HTTPException(status_code=401, detail="Incorrect PIN")
    
    wallet.balance += amount
    db.commit()
    db.refresh(wallet)
    return wallet

def delete_wallet(db: Session, wallet_id: int):
    wallet = get_wallet(db, wallet_id)
    if wallet:
        db.delete(wallet)
        db.commit()
    return wallet

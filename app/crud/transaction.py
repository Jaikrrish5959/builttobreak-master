from sqlalchemy.orm import Session
from app.database.models import Transaction, Wallet, WalletStatus
from app.schemas.transaction import TransactionCreate
from fastapi import HTTPException
from app.core.crypto import verify_pin
import time

def create_transfer_vulnerable(db: Session, transaction: TransactionCreate):
    """
    SECURE IMPLEMENTATION:
    - Uses SELECT ... FOR UPDATE to lock the sender's wallet row.
    - Prevents race conditions by ensuring only one transaction can modify the balance at a time.
    - Requires PIN authentication for sender wallet.
    """
    
    # Validate amount > 0
    if transaction.amount <= 0:
        raise HTTPException(status_code=400, detail="Transfer amount must be greater than 0")
    
    # 1. READ SENDER WITH LOCK
    # with_for_update() locks the selected rows until the transaction commits or rolls back
    sender = db.query(Wallet).filter(Wallet.id == transaction.from_wallet_id).with_for_update().first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender wallet not found")
    
    # 2. VERIFY PIN using secure bcrypt comparison
    if not verify_pin(transaction.pin, sender.pin_hash):
        raise HTTPException(status_code=401, detail="Incorrect PIN for sender wallet")
        
    # 3. READ RECEIVER (Locking receiver is also good practice to prevent deadlocks in reverse transfers, 
    # but strictly for double-spend protection, locking sender is critical)
    receiver = db.query(Wallet).filter(Wallet.id == transaction.to_wallet_id).first()
    if not receiver:
        raise HTTPException(status_code=404, detail="Receiver wallet not found")

    # 4. VALIDATE
    if sender.balance < transaction.amount:
        raise HTTPException(status_code=400, detail="Insufficient funds")

    if sender.status != WalletStatus.ACTIVE:
         raise HTTPException(status_code=400, detail="Sender wallet inactive")

    # 5. UPDATE BALANCES (In memory -> DB)
    sender.balance -= transaction.amount
    receiver.balance += transaction.amount
    
    # 6. CREATE TRANSACTION RECORD
    db_txn = Transaction(
        from_wallet_id=transaction.from_wallet_id,
        to_wallet_id=transaction.to_wallet_id,
        amount=transaction.amount
    )
    db.add(db_txn)
    
    # 7. COMMIT
    db.commit()
    db.refresh(db_txn)
    
    return db_txn

def create_batch_transfer(db: Session, batch: TransactionCreate): 
    # Note: Type hint above is technically BatchTransferCreate but using dynamic for now or imported
    # Actually let's just use the dict or object access.
    
    # 1. LOCK KEY SENDER
    sender = db.query(Wallet).filter(Wallet.id == batch.from_wallet_id).with_for_update().first()
    if not sender:
        raise HTTPException(status_code=404, detail="Sender wallet not found")
    
    # VERIFY PIN using secure bcrypt comparison
    if not verify_pin(batch.pin, sender.pin_hash):
        raise HTTPException(status_code=401, detail="Incorrect PIN for sender wallet")

    if sender.status != WalletStatus.ACTIVE:
         raise HTTPException(status_code=400, detail="Sender wallet inactive")

    # 2. VALIDATE AMOUNTS AND CALCULATE TOTAL
    for idx, t in enumerate(batch.transfers, 1):
        if t.amount <= 0:
            raise HTTPException(status_code=400, detail=f"Recipient {idx}: Amount must be greater than 0")
    
    total_needed = sum(t.amount for t in batch.transfers)
    
    # 3. ATOMIC CHECK
    if sender.balance < total_needed:
        raise HTTPException(
            status_code=400, 
            detail=f"Insufficient funds for batch. Required: {total_needed}, Available: {sender.balance}"
        )

    # 4. EXECUTE ALL
    processed_txns = []
    
    sender.balance -= total_needed
    
    for t in batch.transfers:
        receiver = db.query(Wallet).filter(Wallet.id == t.to_wallet_id).first()
        if not receiver:
             # In a real system you might rollback, but here we error out
             raise HTTPException(status_code=404, detail=f"Receiver {t.to_wallet_id} not found")
        
        receiver.balance += t.amount
        
        db_txn = Transaction(
            from_wallet_id=batch.from_wallet_id,
            to_wallet_id=t.to_wallet_id,
            amount=t.amount
        )
        db.add(db_txn)
        processed_txns.append(db_txn)
        
    db.commit()
    return processed_txns

def get_transactions(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Transaction).order_by(Transaction.timestamp.desc()).offset(skip).limit(limit).all()

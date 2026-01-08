from pydantic import BaseModel, Field, validator
from datetime import datetime

class TransactionBase(BaseModel):
    from_wallet_id: int
    to_wallet_id: int
    amount: float

class TransferTarget(BaseModel):
    to_wallet_id: int
    amount: float

class BatchTransferCreate(BaseModel):
    from_wallet_id: int
    transfers: list[TransferTarget]
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN for sender wallet")
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        if len(v) != 4:
            raise ValueError('PIN must be exactly 4 digits')
        return v

class TransactionCreate(TransactionBase):
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN for sender wallet")
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        if len(v) != 4:
            raise ValueError('PIN must be exactly 4 digits')
        return v

class Transaction(TransactionBase):
    id: int
    timestamp: datetime

    class Config:
        from_attributes = True

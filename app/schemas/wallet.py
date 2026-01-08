from pydantic import BaseModel, Field, validator
from typing import Optional
from app.database.models import WalletStatus

class WalletBase(BaseModel):
    pass

class WalletCreate(WalletBase):
    user_id: int
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN")
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        if len(v) != 4:
            raise ValueError('PIN must be exactly 4 digits')
        return v

class Wallet(WalletBase):
    id: int
    user_id: int
    balance: float
    status: WalletStatus

    class Config:
        from_attributes = True

class WalletDeposit(BaseModel):
    amount: float
    pin: str = Field(..., min_length=4, max_length=4, description="4-digit PIN for authentication")
    
    @validator('pin')
    def validate_pin(cls, v):
        if not v.isdigit():
            raise ValueError('PIN must contain only digits')
        if len(v) != 4:
            raise ValueError('PIN must be exactly 4 digits')
        return v

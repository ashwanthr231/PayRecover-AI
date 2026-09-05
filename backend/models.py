from typing import Literal


from pydantic import BaseModel, Field


PaymentMethod = Literal["UPI", "CARD", "NETBANKING"]
FailureCode = Literal[
    "BANK_TIMEOUT",
    "NETWORK_ERROR",
    "GATEWAY_TIMEOUT",
    "INSUFFICIENT_FUNDS",
    "CARD_DECLINED",
    "FRAUD_SUSPECTED",
    "INVALID_CARD",
    "EXPIRED_CARD",
    "INVALID_ACCOUNT",
    "ACCOUNT_BLOCKED",
]


class Payment(BaseModel):
    payment_id: str = Field(min_length=1, max_length=100)
    merchant_id: str = Field(min_length=1, max_length=100)
    customer_id: str = Field(min_length=1, max_length=100)
    amount: float = Field(gt=0)
    payment_method: PaymentMethod
    failure_code: FailureCode
    attempt_number: int = Field(ge=1, le=4)
    status: Literal["FAILED"] = "FAILED"


class Diagnosis(BaseModel):
    failure_class: str
    confidence: float
    recovery_probability: float
    recommended_action: str
    reason: str

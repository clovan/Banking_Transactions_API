from pydantic import BaseModel
from datetime import datetime

class Transaction(BaseModel):
    id: int
    sender: str
    receiver: str
    amount: float
    date: datetime
    category: str
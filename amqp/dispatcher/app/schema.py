from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel
from uuid import uuid4

class Event(BaseModel):
    id: str = str(uuid4())
    created_at: datetime = datetime.now()
    routed_at: datetime
    raw: str 
    status: str

    class Config:
        orm_mode = True
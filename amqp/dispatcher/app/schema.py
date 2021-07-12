from typing import List, Optional
from datetime import datetime
from pydantic import BaseModel, Field
from uuid import uuid4
from typing_extensions import Annotated

class Event(BaseModel):
    id: Annotated[str, Field(default_factory=lambda: uuid4().hex)]
    created_at: datetime = datetime.now()
    routed_at: datetime
    raw: str 
    status: str

    class Config:
        orm_mode = True
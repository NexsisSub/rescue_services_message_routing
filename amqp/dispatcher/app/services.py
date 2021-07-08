from sqlalchemy.orm import Session

from models import Event as EventModel
from schema import Event as EventSchema

def create_event(db: Session, event: EventSchema):
    print("Start creating event")
    user = EventModel(id=event.id, created_at=event.created_at, raw=event.raw, status=event.status)
    db.add(user)
    db.commit()
    db.refresh(user)
    return user
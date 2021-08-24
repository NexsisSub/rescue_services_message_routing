from schema import Event as EventSchema
from elasticsearch import Elasticsearch
from datetime import datetime 

def create_event(elastic_client: Elasticsearch, event: EventSchema):
    print("Start creating event")
    elastic_client.index(
        index=f"log-dispatcher-{datetime.today().strftime('%Y-%m-%d')}", 
        id=event.id, 
        body=event.json()
    )
    return event
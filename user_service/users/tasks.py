from user_service_config.third_party.celery import app
import json


# Clerk event producer
@app.task
def publish_user_updated(user_id, payload):
    # consumers can perform whatever logic on this event
    return {"user_id": user_id, "payload": payload}

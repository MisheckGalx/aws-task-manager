import uuid
import time
from common import table, response, get_user_id, parse_body


def handler(event, context):
    user_id = get_user_id(event)
    body = parse_body(event)

    title = body.get("title")
    if not title:
        return response(400, {"error": "title is required"})

    task_id = str(uuid.uuid4())
    item = {
        "userId": user_id,
        "taskId": task_id,
        "title": title,
        "description": body.get("description", ""),
        "status": body.get("status", "pending"),
        "createdAt": int(time.time()),
    }

    table.put_item(Item=item)
    return response(201, item)

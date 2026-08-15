from common import table, response, get_user_id


def handler(event, context):
    user_id = get_user_id(event)
    task_id = event["pathParameters"]["taskId"]

    existing = table.get_item(Key={"userId": user_id, "taskId": task_id}).get("Item")
    if not existing:
        return response(404, {"error": "task not found"})

    table.delete_item(Key={"userId": user_id, "taskId": task_id})
    return response(204, {})

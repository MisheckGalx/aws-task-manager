from common import table, response, get_user_id


def handler(event, context):
    user_id = get_user_id(event)
    task_id = event["pathParameters"]["taskId"]

    result = table.get_item(Key={"userId": user_id, "taskId": task_id})
    item = result.get("Item")

    if not item:
        return response(404, {"error": "task not found"})

    return response(200, item)

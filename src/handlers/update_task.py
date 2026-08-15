from common import table, response, get_user_id, parse_body

ALLOWED_FIELDS = {"title", "description", "status"}


def handler(event, context):
    user_id = get_user_id(event)
    task_id = event["pathParameters"]["taskId"]
    body = parse_body(event)

    updates = {k: v for k, v in body.items() if k in ALLOWED_FIELDS}
    if not updates:
        return response(400, {"error": "no valid fields to update"})

    existing = table.get_item(Key={"userId": user_id, "taskId": task_id}).get("Item")
    if not existing:
        return response(404, {"error": "task not found"})

    expr_names = {f"#{k}": k for k in updates}
    expr_values = {f":{k}": v for k, v in updates.items()}
    update_expr = "SET " + ", ".join(f"#{k} = :{k}" for k in updates)

    result = table.update_item(
        Key={"userId": user_id, "taskId": task_id},
        UpdateExpression=update_expr,
        ExpressionAttributeNames=expr_names,
        ExpressionAttributeValues=expr_values,
        ReturnValues="ALL_NEW",
    )

    return response(200, result["Attributes"])

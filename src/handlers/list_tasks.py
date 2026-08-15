from boto3.dynamodb.conditions import Key
from common import table, response, get_user_id


def handler(event, context):
    user_id = get_user_id(event)

    result = table.query(
        KeyConditionExpression=Key("userId").eq(user_id)
    )

    return response(200, {"tasks": result.get("Items", [])})

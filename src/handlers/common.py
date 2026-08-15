"""Shared utilities used by every Lambda handler."""
import json
import os
from decimal import Decimal
import boto3


class DecimalEncoder(json.JSONEncoder):
    """DynamoDB returns numeric types as Decimal; make them JSON-safe."""

    def default(self, o):
        if isinstance(o, Decimal):
            return int(o) if o % 1 == 0 else float(o)
        return super().default(o)

TABLE_NAME = os.environ.get("TABLE_NAME")
_dynamodb = boto3.resource("dynamodb")
table = _dynamodb.Table(TABLE_NAME) if TABLE_NAME else None

CORS_HEADERS = {
    "Access-Control-Allow-Origin": "*",
    "Access-Control-Allow-Headers": "Content-Type,Authorization",
    "Access-Control-Allow-Methods": "GET,POST,PUT,DELETE,OPTIONS",
}


def response(status_code: int, body: dict) -> dict:
    """Build a proper API Gateway proxy-integration response."""
    return {
        "statusCode": status_code,
        "headers": {**CORS_HEADERS, "Content-Type": "application/json"},
        "body": json.dumps(body, cls=DecimalEncoder),
    }


def get_user_id(event: dict) -> str:
    """
    Pull the caller's identity from the request.

    In production this should come from a Cognito authorizer claim
    (event['requestContext']['authorizer']['claims']['sub']).
    For now, fall back to a header so the API is easy to test with curl.
    """
    try:
        return event["requestContext"]["authorizer"]["claims"]["sub"]
    except (KeyError, TypeError):
        return event.get("headers", {}).get("x-user-id", "demo-user")


def parse_body(event: dict) -> dict:
    try:
        return json.loads(event.get("body") or "{}")
    except json.JSONDecodeError:
        return {}

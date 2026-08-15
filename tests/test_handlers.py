"""
Local unit tests — no AWS account needed.
Run with: pytest tests/ -v
"""
import os
import json
import sys
import boto3
import pytest
from moto import mock_aws

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src", "handlers"))

TABLE_NAME = "tasks-test"
os.environ["TABLE_NAME"] = TABLE_NAME
os.environ.setdefault("AWS_DEFAULT_REGION", "us-east-1")
os.environ.setdefault("AWS_ACCESS_KEY_ID", "testing")
os.environ.setdefault("AWS_SECRET_ACCESS_KEY", "testing")


@pytest.fixture
def dynamodb_table():
    with mock_aws():
        client = boto3.resource("dynamodb", region_name="us-east-1")
        client.create_table(
            TableName=TABLE_NAME,
            AttributeDefinitions=[
                {"AttributeName": "userId", "AttributeType": "S"},
                {"AttributeName": "taskId", "AttributeType": "S"},
            ],
            KeySchema=[
                {"AttributeName": "userId", "KeyType": "HASH"},
                {"AttributeName": "taskId", "KeyType": "RANGE"},
            ],
            BillingMode="PAY_PER_REQUEST",
        )
        import importlib
        import common
        importlib.reload(common)
        yield common.table


def _event(body=None, path_params=None, headers=None):
    return {
        "body": json.dumps(body) if body is not None else None,
        "pathParameters": path_params or {},
        "headers": headers or {"x-user-id": "test-user"},
        "requestContext": {},
    }


def test_create_and_get_task(dynamodb_table):
    import create_task, get_task

    create_resp = create_task.handler(_event(body={"title": "Learn AWS SAM"}), None)
    assert create_resp["statusCode"] == 201
    created = json.loads(create_resp["body"])
    assert created["title"] == "Learn AWS SAM"

    get_resp = get_task.handler(_event(path_params={"taskId": created["taskId"]}), None)
    assert get_resp["statusCode"] == 200
    assert json.loads(get_resp["body"])["taskId"] == created["taskId"]


def test_get_missing_task_returns_404(dynamodb_table):
    import get_task
    resp = get_task.handler(_event(path_params={"taskId": "does-not-exist"}), None)
    assert resp["statusCode"] == 404


def test_list_tasks(dynamodb_table):
    import create_task, list_tasks

    create_task.handler(_event(body={"title": "Task 1"}), None)
    create_task.handler(_event(body={"title": "Task 2"}), None)

    resp = list_tasks.handler(_event(), None)
    body = json.loads(resp["body"])
    assert len(body["tasks"]) == 2


def test_update_task(dynamodb_table):
    import create_task, update_task

    created = json.loads(create_task.handler(_event(body={"title": "Old"}), None)["body"])
    resp = update_task.handler(
        _event(body={"status": "done"}, path_params={"taskId": created["taskId"]}), None
    )
    assert resp["statusCode"] == 200
    assert json.loads(resp["body"])["status"] == "done"


def test_delete_task(dynamodb_table):
    import create_task, delete_task, get_task

    created = json.loads(create_task.handler(_event(body={"title": "Bye"}), None)["body"])
    del_resp = delete_task.handler(_event(path_params={"taskId": created["taskId"]}), None)
    assert del_resp["statusCode"] == 204

    get_resp = get_task.handler(_event(path_params={"taskId": created["taskId"]}), None)
    assert get_resp["statusCode"] == 404

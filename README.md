# aws-task-manager — Serverless REST API

A CRUD REST API for managing tasks, built entirely on AWS: API Gateway -> Lambda (Python) -> DynamoDB. No servers to patch, scales to zero, pay only per request.

## Architecture

Client -> API Gateway -> Lambda (per route) -> DynamoDB (tasks table), with CloudWatch Logs collecting Lambda output.

- API Gateway: REST API, routes each HTTP method to its own Lambda.
- Lambda: one small function per operation (create/list/get/update/delete), each with a scoped IAM role.
- DynamoDB: single table, userId as partition key, taskId as sort key. Listing a user's tasks is one efficient Query, not a full table Scan.

## Why this pattern (solutions-architect view)

- Single-table design (userId as PK, taskId as SK) avoids expensive table scans as data grows.
- One Lambda per route: smaller blast radius, independent scaling, tighter IAM permissions per function.
- PAY_PER_REQUEST billing on DynamoDB: no capacity planning needed for a project at this stage.
- Auth stub: get_user_id() currently reads an x-user-id header for easy curl testing. Swap in a real Cognito authorizer before production use.

## Run tests locally (no AWS needed)

python3 -m venv venv
source venv/bin/activate
pip install boto3 moto pytest
pytest tests/ -v

All 5 tests mock DynamoDB with moto, so handler logic can be verified without touching AWS.

## Deploy

sam build
sam deploy --guided

## Status

Deployed and verified end-to-end (create, list, get, update, delete) against a live AWS stack in eu-central-1.

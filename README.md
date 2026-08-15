# aws-task-manager

A serverless REST API for managing tasks — built as a hands-on project to learn how API Gateway, Lambda, and DynamoDB fit together on AWS.

It's a simple idea on purpose: create, list, get, update, and delete tasks. The point wasn't the app itself — it was building and deploying a real serverless backend from scratch, end to end, no shortcuts.

## Architecture

A request comes in through API Gateway, gets routed to the right Lambda function based on the HTTP method and path, and that function reads or writes to a DynamoDB table. Every Lambda has its own scoped IAM role — it can only touch the one table it needs, nothing else.

![Architecture diagram](docs/screenshots/serverless_rest_api_architecture.png)

## What it actually looks like, deployed

**CloudFormation created every piece of infrastructure from one template — no manual clicking around the console.**

![CloudFormation stack](docs/screenshots/cloudformation.png)

**Five Lambda functions, one per operation, each independently deployable and independently permissioned.**

![Lambda functions](docs/screenshots/lambda.png)

**The DynamoDB table, holding real task data created through the live API.**

![DynamoDB table](docs/screenshots/dynamodb.png)

**API Gateway's resource tree — /tasks and /tasks/{taskId}, wired to their Lambda functions.**

![API Gateway resources](docs/screenshots/api-gateway.png)

## Why it's built this way

- **`userId` + `taskId` as the DynamoDB key**: this lets me fetch all of one user's tasks with a single, cheap `Query` — not a full table scan. That one decision is the difference between a table that stays fast as it grows and one that doesn't.
- **One Lambda per route, not one big function**: each function does one thing, has its own minimal IAM permissions, and can be changed or redeployed without touching the others.
- **Pay-per-request billing**: no capacity planning needed at this stage — cost scales with actual usage, not provisioned capacity sitting idle.
- **Auth is currently a header stub** (`x-user-id`), specifically so I could test the whole flow with `curl` before wiring up real authentication. Swapping in Cognito is the next step, not an afterthought — the code path for it is already there.


sam build
sam deploy --guided

## Status

Deployed and verified end-to-end (create, list, get, update, delete) against a live AWS stack in eu-central-1.

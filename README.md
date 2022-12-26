# SJ57 API

This is a Python 3 CDK project that deploys a REST API to AWS. The API has a single endpoint which invokes a Lambda function to open a garage door.

## Requirements

- AWS CLI
- AWS CDK
- Python 3

## Environment Variables

The following environment variables must be set before deploying the stack:

- `DISCORD_WEBHOOK`: Discord webhook URL for sending notifications
- `AWS_REGION`: AWS region to deploy the stack to
- `AWS_ACCESS_KEY_ID`: AWS access key ID with permissions to deploy the stack
- `AWS_SECRET_ACCESS_KEY`: AWS secret access key corresponding to the access key ID
- `AWS_CDK_ACCOUNT_ID`: AWS account ID for the stack

## Deployment

1. Run `cdk synth` to generate the CloudFormation template
2. Run `cdk deploy` to deploy the stack

## Testing

To test the API, send a `POST` request to the `/open-garage` endpoint with an empty body. A notification will be sent to the Discord webhook specified in the `DISCORD_WEBHOOK` environment variable and the garage door will be opened (if it is connected to the system).

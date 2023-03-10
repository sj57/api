#!/usr/bin/env python3

import dotenv

dotenv.load_dotenv()

import aws_cdk
from aws_cdk import aws_lambda, aws_apigateway
from aws_cdk import Stack
from aws_cdk import aws_certificatemanager
from aws_cdk import aws_logs
from aws_cdk import aws_route53_targets
from aws_cdk import aws_route53
from constructs import Construct
import os

STACK_NAME = "sj57-api"
DOMAIN_NAME = "sj57.info"
DISCORD_WEBHOOK = os.environ['DISCORD_WEBHOOK']
AWS_REGION = os.environ['AWS_REGION']
AWS_ACCESS_KEY_ID = os.environ['AWS_ACCESS_KEY_ID']
AWS_SECRET_ACCESS_KEY = os.environ['AWS_SECRET_ACCESS_KEY']
AWS_CDK_ACCOUNT_ID = os.environ['AWS_CDK_ACCOUNT_ID']
API_KEY = os.environ['API_KEY']

LAMBDA_FUNCTION_TIMEOUT_SECONDS = 5
MEMORY_SIZE_MEGABYTES = 128
SCRIPT_DIR = os.path.realpath(os.path.dirname(__file__))


class SJ57CdkStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        open_garage_lambda_handler = aws_lambda.Function(
            self,
            f'{STACK_NAME}-open-garage-lambda',
            function_name=f'{STACK_NAME}-open-garage-lambda',
            code=aws_lambda.Code.from_asset(SCRIPT_DIR, exclude=['.idea', '.git', 'cdk.out']),
            handler="handler.handler_open_garage",
            timeout=aws_cdk.Duration.seconds(LAMBDA_FUNCTION_TIMEOUT_SECONDS),
            memory_size=MEMORY_SIZE_MEGABYTES,
            runtime=aws_lambda.Runtime.PYTHON_3_8,
            environment={
                "DISCORD_WEBHOOK": DISCORD_WEBHOOK,
                "API_KEY": API_KEY,
            },
            retry_attempts=0,
            log_retention=aws_logs.RetentionDays.ONE_MONTH,
        )

        hosted_zone = aws_route53.HostedZone.from_lookup(self, "HostedZone", domain_name=DOMAIN_NAME)
        api_domain_name = f"api.{DOMAIN_NAME}"
        certificate = aws_certificatemanager.DnsValidatedCertificate(
            self,
            f'{STACK_NAME}-rest-api-certificate',
            domain_name=api_domain_name,
            hosted_zone=hosted_zone
        )

        rest_api = aws_apigateway.RestApi(
            self,
            f'{STACK_NAME}-rest-api',
            rest_api_name=f'{STACK_NAME}-rest-api',
            cloud_watch_role=True,
            domain_name=aws_apigateway.DomainNameOptions(
                domain_name=api_domain_name,
                certificate=certificate,
                security_policy=aws_apigateway.SecurityPolicy.TLS_1_2
            ),
            default_cors_preflight_options=aws_apigateway.CorsOptions(
                allow_origins=aws_apigateway.Cors.ALL_ORIGINS,
                allow_headers=[
                    'Content-Type',
                    'X-Amz-Date',
                    'Authorization',
                    'X-Api-Key',
                ],
                allow_credentials=True,
                allow_methods=['OPTIONS', 'GET', 'POST', 'PUT', 'HEAD', 'DELETE'],
            ),
            endpoint_types=[aws_apigateway.EndpointType.REGIONAL],
            deploy_options=aws_apigateway.StageOptions(
                metrics_enabled=True,
                logging_level=aws_apigateway.MethodLoggingLevel.INFO,
                data_trace_enabled=True,
                stage_name='prod'
            ))

        open_garage_lambda_integration = aws_apigateway.LambdaIntegration(open_garage_lambda_handler)
        rest_api.root.add_resource("v1").add_resource("garage").add_method("POST", open_garage_lambda_integration)

        aws_route53.ARecord(
            self,
            f'{STACK_NAME}-rest-api-record',
            record_name="api",
            zone=hosted_zone,
            target=aws_route53.RecordTarget.from_alias(aws_route53_targets.ApiGateway(rest_api)),
        )

        print(rest_api.url)


if __name__ == '__main__':
    app = aws_cdk.App()
    SJ57CdkStack(app, STACK_NAME, env={
        'account': AWS_CDK_ACCOUNT_ID,
        'region': AWS_REGION
    })
    app.synth()

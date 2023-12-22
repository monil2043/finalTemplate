#!/usr/bin/env python3
import os
import re

from aws_cdk import App, Environment
from boto3 import client, session

from cdk.{{cookiecutter.service_name}}.service_stack import ServiceStack


def modify_stack_name(user_input):
    # Define the regex pattern for a valid AWS CloudFormation stack name
    stack_name_pattern = re.compile(r'^[A-Za-z][A-Za-z0-9-]*$')

    # Remove invalid characters (replace underscores with hyphens)
    modified_name = re.sub(r'[^A-Za-z0-9-]', '-', user_input)

    # Ensure the modified name adheres to the stack name pattern
    if stack_name_pattern.match(modified_name):
        return modified_name
    else:
        # If the modified name still doesn't match, use a default value
        return 'DeployLambdaStack'




account = client('sts').get_caller_identity()['Account']
region = session.Session().region_name
environment = os.getenv('ENVIRONMENT', 'dev')
app = App()
my_stack = ServiceStack(
    scope=app,
    id=modify_stack_name('{{cookiecutter.lambda_name}}Stack'),
    env=Environment(account=os.environ.get('AWS_DEFAULT_ACCOUNT', account), region=os.environ.get('AWS_DEFAULT_REGION', region)),
    is_production_env=True if environment == 'production' else False,
    ssmParamName = '/mercury/backendIntegration/appConfigUrl'
)

app.synth()

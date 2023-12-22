import json
import os
import boto3
from botocore.exceptions import NoCredentialsError
from mercuryReusableMethods.commonDependency import (
    call_api,
    create_correlation_id,
    handle_bad_request,
    handle_forbidden,
    handle_internal_server_error,
    handle_not_acceptable,
    handle_not_found,
    handle_success,
    handle_unauthorized,
    log_request_received,
    log_response_received,
    parse_and_print_json,
    parse_and_print_xml,
)
from aws_lambda_powertools import Logger, Metrics, Tracer
tracer = Tracer()
logger = Logger()
metrics = Metrics()
parameter_name = os.environ.get('MY_PARAMETER_ENV_VAR')
def getAppConfigUrl():
    try:
        # Create an SSM client
        ssm_client = boto3.client('ssm')

        # Get the parameter value
        response = ssm_client.get_parameter(
            Name=parameter_name,
            WithDecryption=True  # Decrypt the parameter value if it's encrypted
        )

        # Extract the parameter value
        parameter_value = response['Parameter']['Value']

        # Log or process the parameter value as needed
        print(f"Parameter Value: {parameter_value}")

        # Return a response
        return parameter_value

    except NoCredentialsError:
        # Handle credential-related errors
        return {
            'statusCode': 500,
            'body': json.dumps({'error': 'AWS credentials not available'})
        }

    except Exception as e:
        # Handle other exceptions
        return {
            'statusCode': 500,
            'body': json.dumps({'error': str(e)})
        }
def isFeatureEnabled():
    # Call feature flag to get down the values noted
    featureFlagResponseJsonContent = call_api(getAppConfigUrl(), 'GET')[1]
    config_data = json.loads(featureFlagResponseJsonContent)
    customerProfileImplemented = config_data.get('enableCustomerProfile', {}).get('enabled', True)
    customerProfileBackendURL = config_data.get('customerProfileConfig', {}).get('backendAPIUrl', '')
    return customerProfileImplemented, customerProfileBackendURL



def appendQueryParams(base_url, params):
    url = base_url + "?" + "&".join([f"{key}={value}" for key, value in params.items()])
    return url

@tracer.capture_lambda_handler(capture_response=False)
def lambda_handler(event, context):
    log_request_received(event)

    isFeatureFlagEnabled, customerProfileBackendURL = isFeatureEnabled()

    base_url = customerProfileBackendURL
    params = {
        "keyType": event['queryStringParameters']['keyType'],
        "keyValue": event['queryStringParameters']['keyValue']
    }

    getCustomerProfileURL = appendQueryParams(base_url,params)

    if isFeatureFlagEnabled:
        statusCodeValue, body, headerValue = (
            call_api(getCustomerProfileURL, 'GET'))
        return {'statusCode': statusCodeValue, 'body': body, 'headers': headerValue}
    else:
        return handle_not_found('method not found')
    


    # To make a post call, use following format for call_api
    # pass in json data 
    # call_api(Url, 'POST', data))
    # data = json.dumps({"key":"value"})


if __name__ == '__main__':
    (lambda_handler(event, None))

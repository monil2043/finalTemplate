import os
import sys
import unittest
from unittest.mock import Mock, patch

script_directory = os.path.dirname(os.path.abspath(__file__))
new_path = script_directory.replace("tests/unit", "{{cookiecutter.service_name}}")
new_path = os.path.abspath(new_path)
sys.path.append(new_path)
from lambda_function import lambda_handler


class TestLambdaHandler(unittest.TestCase):

    @patch('lambda_function.call_api')
    def test_lambda_handler_get_customer_profile_success(self, mock_call_api):

        mock_response = Mock()
        # Mock the first call_api function to return a 200 response
        mock_call_api.return_value = [200, '{"performActionImplemented": {"enabled":"true"}}', {'Content-Type': 'application/json'}]

        # Create a sample event
        event = {
            'version': '2.0',
            'routeKey': '$default',
            'rawPath': '/address',
            'rawQueryString': 'methodToCall=GetCustomerProfile&phoneNumber=1234',
            'headers': {
                # Your headers here
            },
            'queryStringParameters': {
                'keyType': 'phoneNumber',
                'keyValue': 1234
            },
            'requestContext': {
                # Your request context here
            },
            'isBase64Encoded': False
        }

        # Call the lambda_handler function
        response = lambda_handler(event, None)

        # Assertions for the response
        self.assertEqual(response['statusCode'], 200)
        self.assertEqual(response['body'], '{"performActionImplemented": {"enabled":"true"}}')
        self.assertEqual(response['headers'], {'Content-Type': 'application/json'})


if __name__ == '__main__':
    unittest.main()

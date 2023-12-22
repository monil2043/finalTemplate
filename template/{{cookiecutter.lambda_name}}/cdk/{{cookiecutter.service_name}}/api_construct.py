from aws_cdk import Duration, RemovalPolicy
from aws_cdk import aws_iam as iam
from aws_cdk import aws_lambda as _lambda
from aws_cdk.aws_lambda import LayerVersion
from aws_cdk.aws_lambda_python_alpha import PythonLayerVersion
from aws_cdk.aws_logs import RetentionDays
from constructs import Construct
from aws_cdk import aws_ssm as ssm

import cdk.{{cookiecutter.service_name}}.constants as constants
from cdk.{{cookiecutter.service_name}}.monitoring import CrudMonitoring

class ApiConstruct(Construct):

    def __init__(self, scope: Construct, id_: str, ssmParamName: str) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self.lambda_role = self._build_lambda_role()
        self.common_layer = self._build_common_layer()
        self.create_address_validation = self._add_lambda_integration(self.lambda_role, ssmParamName)
        self.monitoring = CrudMonitoring(self, id_, [self.create_address_validation])

    def _build_lambda_role(self) -> iam.Role:
        return iam.Role(
            self,
            constants.SERVICE_ROLE_ARN,
            assumed_by=iam.ServicePrincipal('lambda.amazonaws.com'),
            inline_policies={
                'dynamic_configuration':
                    iam.PolicyDocument(statements=[
                        iam.PolicyStatement(
                            actions=['appconfig:GetLatestConfiguration', 'appconfig:StartConfigurationSession'],
                            resources=['*'],
                            effect=iam.Effect.ALLOW,
                        )
                    ]),
                'appconfig_full_access':  # Add the appConfig_fullAccess policy
                    iam.PolicyDocument(statements=[iam.PolicyStatement(
                        actions=['appconfig:*'],
                        resources=['*'],
                        effect=iam.Effect.ALLOW,
                    )]),
                'ssm_parameter_access':  # New policy for SSM Parameter Store access
                    iam.PolicyDocument(statements=[iam.PolicyStatement(
                        actions=['ssm:GetParameter'],
                        resources=['*'],  # Specify the ARN of the SSM parameter
                        effect=iam.Effect.ALLOW,
                )]),
            },
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(managed_policy_name=(f'service-role/{constants.LAMBDA_BASIC_EXECUTION_ROLE}'))
            ],
        )

    def _build_common_layer(self) -> LayerVersion:
        return LayerVersion(
            self,
            f'{self.id_}{constants.LAMBDA_LAYER_NAME}',
            #entry=constants.COMMON_LAYER_BUILD_FOLDER,
            code=_lambda.Code.from_asset(constants.LAYER_FOLDER),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_12],
            removal_policy=RemovalPolicy.DESTROY,
        )

    def _add_lambda_integration(
        self,
        role: iam.Role,
        ssmParamName
    ) -> _lambda.Function:

        appconfig_layer = LayerVersion.from_layer_version_arn(
            self, f'{self.id_}AppConfigLayer', layer_version_arn='arn:aws:lambda:us-east-1:027255383542:layer:AWS-AppConfig-Extension:113')
        lambda_function = _lambda.Function(
            self,
            constants.CREATE_LAMBDA,
            function_name='{{cookiecutter.lambda_name}}',
            runtime=_lambda.Runtime.PYTHON_3_12,
            code=_lambda.Code.from_asset(constants.BUILD_FOLDER),
            handler='lambda_function.lambda_handler',
            environment={
                constants.POWERTOOLS_SERVICE_NAME: constants.SERVICE_NAME,  # for logger, tracer and metrics
                constants.POWER_TOOLS_LOG_LEVEL: 'DEBUG',  # for logger
                #'CONFIGURATION_APP': appconfig_app_name,  # for feature flags
                'CONFIGURATION_ENV': constants.ENVIRONMENT,  # for feature flags
                'CONFIGURATION_NAME': constants.CONFIGURATION_NAME,  # for feature flags
                'CONFIGURATION_MAX_AGE_MINUTES': constants.CONFIGURATION_MAX_AGE_MINUTES,  # for feature flags
                #'REST_API': 'https://apibaseurl/api',  # for env vars example
                'ROLE_ARN': 'arn:partition:service:region:account-id:resource-type:resource-id',  # for env vars example
                'MY_PARAMETER_ENV_VAR': ssmParamName
            },
            tracing=_lambda.Tracing.ACTIVE,
            retry_attempts=0,
            timeout=Duration.seconds(constants.API_HANDLER_LAMBDA_TIMEOUT),
            memory_size=constants.API_HANDLER_LAMBDA_MEMORY_SIZE,
            layers=[self.common_layer, appconfig_layer],
            role=role,
        )
        return lambda_function

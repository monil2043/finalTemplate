import aws_cdk.aws_sns as sns
from aws_cdk import CfnOutput, Duration, aws_apigateway
from aws_cdk import aws_dynamodb as dynamodb
from aws_cdk import aws_iam as iam
from aws_cdk import aws_kms as kms
from aws_cdk import aws_lambda as _lambda
from cdk_monitoring_constructs import (
    AlarmFactoryDefaults,
    CustomMetricGroup,
    ErrorRateThreshold,
    LatencyThreshold,
    MetricStatistic,
    MonitoringFacade,
    SnsAlarmActionStrategy,
)
from constructs import Construct

from cdk.{{cookiecutter.service_name}} import constants


class CrudMonitoring(Construct):

    def __init__(
        self,
        scope: Construct,
        id_: str,
        functions: list[_lambda.Function],
    ) -> None:
        super().__init__(scope, id_)
        self.id_ = id_
        self._build_low_level_dashboard(functions, self.notification_topic)

    
    def _build_low_level_dashboard(self, functions: list[_lambda.Function]):
        low_level_facade = MonitoringFacade(
            self,
            f'{self.id_}LowFacade',
            alarm_factory_defaults=AlarmFactoryDefaults(
                actions_enabled=True,
                alarm_name_prefix=self.id_
            ),
        )
        low_level_facade.add_large_header('Orders REST API Low Level Dashboard')
        for func in functions:
            low_level_facade.monitor_lambda_function(
                lambda_function=func,
                add_latency_p90_alarm={'p90': LatencyThreshold(max_latency=Duration.seconds(3))},
            )
            low_level_facade.monitor_log(
                log_group_name=func.log_group.log_group_name,
                human_readable_name='Error logs',
                pattern='ERROR',
                alarm_friendly_name='error logs',
            )
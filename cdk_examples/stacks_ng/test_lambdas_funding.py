from .modules.lambda_function import DockerLambda
from .modules.sqs_queue import SQSQueue
from .modules.cloudwatch_event import CWEventRuleCron
from constructs import Construct
from aws_cdk import (
  Stack as stack,
  Duration,
  CfnOutput,
  Fn
)
from aws_cdk.aws_lambda_event_sources import SqsEventSource


class Stack(stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.scope = scope
        self.construct_id = construct_id

        # Importing SNS arn that is getting used with cloudwatch alarm for DLQ
        alarm_sns_arn = Fn.import_value('test-sns-dlq-'+environment)

        self.funding_requests_function = \
            DockerLambda(
                self,
                "funding-requests-function",
                environment=environment,
                ecr_name="test-funding-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Funding.Aws::test.Funding.Aws.FundingRequestsFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=alarm_sns_arn
            )

        self.funding_payments_function = \
            DockerLambda(
                self,
                "funding-payments-function",
                environment=environment,
                ecr_name="test-funding-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Funding.Aws::test.Funding.Aws.PaymentsFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=alarm_sns_arn
            )

        self.timing_monitor_function = \
            DockerLambda(
                self,
                "funding-timing-monitor-function",
                environment=environment,
                ecr_name="test-funding-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Funding.Aws::test.Funding.Aws.TimingMonitorFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        # Creating SQS for funding-requests and setting up event for function
        self.funding_requests_queue = SQSQueue(
            self,
            "funding-requests-queue",
            environment=environment,
            queue_name="funding-batches",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_funding_requests = SqsEventSource(
            self.funding_requests_queue.queue
        )
        self.funding_requests_function.function.add_event_source(
            self.sqs_event_funding_requests
        )

        # Creating SQS for payment and setting up event for function
        self.payments_queue = SQSQueue(
            self,
            "funding-payments-queue",
            environment=environment,
            queue_name="payment-funding",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_payments = SqsEventSource(
            self.payments_queue.queue
        )
        self.funding_payments_function.function.add_event_source(
            self.sqs_event_payments
        )

        # For Timing Monitor
        self.timing_monitor_rule = CWEventRuleCron(
            self,
            "funding-timing-monitor-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["timing_monitor"]["enabled"],
            lambda_arn=self.timing_monitor_function.function.function_arn,
            lambda_name=self.timing_monitor_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["timing_monitor"]["rate_limit"],
            rule_name="funding-timing-monitor"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="funding-requests-function-arn",
            value=self.funding_requests_function.function.function_arn,
            export_name="test-funding-requests-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="funding-payments-function-arn",
            value=self.funding_payments_function.function.function_arn,
            export_name="test-funding-payments-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="funding-timing-monitor-function-arn",
            value=self.timing_monitor_function.function.function_arn,
            export_name="test-funding-timing-monitor-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="funding-requests-function-name",
            value=self.funding_requests_function.function.function_name,
            export_name="test-funding-requests-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="funding-payments-function-name",
            value=self.funding_payments_function.function.function_name,
            export_name="test-funding-payments-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="funding-timing-monitor-function-name",
            value=self.timing_monitor_function.function.function_name,
            export_name="test-funding-timing-monitor-function-name" +
            "-" + environment
        )

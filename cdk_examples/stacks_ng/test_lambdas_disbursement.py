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

        self.disbursement_batches_function = \
            DockerLambda(
                self,
                "disbursement-batches-function",
                environment=environment,
                ecr_name="test-disbursement-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Disbursement.Aws::test.Disbursement.Aws.DisbursementBatchesFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=alarm_sns_arn
            )

        self.disbursement_payments_function = \
            DockerLambda(
                self,
                "disbursement-payments-function",
                environment=environment,
                enabled=metadata.get(
                    "event_rules"
                )["disbursement-payments"]["enabled"],
                ecr_name="test-disbursement-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Disbursement.Aws::test.Disbursement.Aws.PaymentsFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get(
                    "event_rules"
                )["disbursement-payments"]["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=alarm_sns_arn
            )

        self.timing_monitor_function = \
            DockerLambda(
                self,
                "disbursement-timing-monitor-function",
                environment=environment,
                ecr_name="test-disbursement-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Disbursement.Aws::test.Disbursement.Aws.TimingMonitorFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        # Creating SQS for disbursement-batches and
        # setting up event for function
        self.disbursement_batches_queue = SQSQueue(
            self,
            "disbursement-batches-queue",
            environment=environment,
            queue_name="disbursement-batches",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_disbursement_batches = SqsEventSource(
            self.disbursement_batches_queue.queue
        )
        self.disbursement_batches_function.function.add_event_source(
            self.sqs_event_disbursement_batches
        )

        # Creating SQS for payment and setting up event for function
        self.payments_queue = SQSQueue(
            self,
            "disbursement-payments-queue",
            environment=environment,
            queue_name="payment-disbursing",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_payments = SqsEventSource(
            self.payments_queue.queue
        )
        self.disbursement_payments_function.function.add_event_source(
            self.sqs_event_payments
        )

        # For Timing Monitor
        self.timing_monitor_rule = CWEventRuleCron(
            self,
            "disbursement-timing-monitor-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["timing_monitor"]["enabled"],
            lambda_arn=self.timing_monitor_function.function.function_arn,
            lambda_name=self.timing_monitor_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["timing_monitor"]["rate_limit"],
            rule_name="disbursement-timing-monitor"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="disbursement-batches-function-arn",
            value=self.disbursement_batches_function.function.function_arn,
            export_name="test-disbursement-batches-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="disbursement-payments-function-arn",
            value=self.disbursement_payments_function.function.function_arn,
            export_name="test-disbursement-payments-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="disbursement-timing-monitor-function-arn",
            value=self.timing_monitor_function.function.function_arn,
            export_name="test-disbursement-timing-monitor-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="disbursement-batches-function-name",
            value=self.disbursement_batches_function.function.function_name,
            export_name="test-disbursement-batches-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="disbursement-payments-function-name",
            value=self.disbursement_payments_function.function.function_name,
            export_name="test-disbursement-payments-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="disbursement-timing-monitor-function-name",
            value=self.timing_monitor_function.function.function_name,
            export_name="test-disbursement-timing-monitor-function-name" +
            "-" + environment
        )

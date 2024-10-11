from .modules.lambda_function import DockerLambda
from .modules.sqs_queue import SQSQueue
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

        self.payment_status_notification_function = \
            DockerLambda(
                self,
                "webhook-payment-status-notification-function",
                environment=environment,
                ecr_name="test-webhooks-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Webhooks.Aws::test.Webhooks.Aws.PaymentStatusNotificationFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=alarm_sns_arn
            )

        # Creating SQS for notification-sets and setting up event for function
        self.payment_status_notification_queue = SQSQueue(
            self,
            "webhooks-payment-status-notification",
            environment=environment,
            queue_name="payment-status-notification",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_payment_status_notification = SqsEventSource(
            self.payment_status_notification_queue.queue
        )
        self.payment_status_notification_function.function.add_event_source(
            self.sqs_event_payment_status_notification
        )

        CfnOutput(
            scope=self,
            id="webhook-payment-status-notification-function-arn",
            value=self.payment_status_notification_function.function.function_arn, # noqa
            export_name="test-webhook-payment-status-notification-function-arn" + # noqa
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="webhook-payment-status-notification-function-name",
            value=self.payment_status_notification_function.function.function_name, # noqa
            export_name="test-webhook-payment-status-notification-function-name" + # noqa
            "-" + environment
        )

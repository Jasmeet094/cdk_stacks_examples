from .modules.lambda_function import DockerLambda
from .modules.sqs_queue import SQSQueue
from .modules.cloudwatch_event import CWEventRuleCron
from constructs import Construct
from aws_cdk import (
  Stack as stack,
  Duration,
  CfnOutput,
  aws_sns as sns
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

        # Create the SNS topic to send DLQ notification
        self.sns_topic = sns.Topic(
            self,
            "test-sns-dlq-"+environment,
            display_name="test-sns-dlq-"+environment,
            topic_name="test-sns-dlq-"+environment
        )

        # Creating SNS Subscriptions
        email_sns_endpoint = metadata.get('lambdas')['email_sns_endpoint']
        for email_address in email_sns_endpoint:
            sns.Subscription(
                self,
                "sns-dlq-sub"+str(email_sns_endpoint.index(email_address))+"-"+environment, # noqa
                endpoint=email_address,
                protocol=sns.SubscriptionProtocol.EMAIL,
                topic=self.sns_topic
            )

        self.compliance_scanner_function = \
            DockerLambda(
                self,
                "compliance-scanner-function",
                environment=environment,
                ecr_name="test-compliance-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                cmd=["test.Compliance.Aws::test.Compliance.Aws.ComplianceScannerFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                region=metadata.get("region"),
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=self.sns_topic.topic_arn
            )

        self.timing_monitor_function = \
            DockerLambda(
                self,
                "compliance-timing-monitor-function",
                environment=environment,
                ecr_name="test-compliance-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Compliance.Aws::test.Compliance.Aws.TimingMonitorFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        # Creating SQS for compliance queue and setting up event for function
        self.compliance_queue = SQSQueue(
            self,
            "compliance-queue",
            environment=environment,
            queue_name="payment-compliance",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_compliance = SqsEventSource(
            self.compliance_queue.queue
        )
        self.compliance_scanner_function.function.add_event_source(
            self.sqs_event_compliance
        )

        # For Timing Monitor
        self.timing_monitor_rule = CWEventRuleCron(
            self,
            "compliance-timing-monitor-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["timing_monitor"]["enabled"],
            lambda_arn=self.timing_monitor_function.function.function_arn,
            lambda_name=self.timing_monitor_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["compliance_timing_monitor"]["rate_limit"],
            rule_name="compliance-timing-monitor"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="compliance-scanner-function-arn",
            value=self.compliance_scanner_function.function.function_arn,
            export_name="test-compliance-scanner-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="compliance-timing-monitor-function-arn",
            value=self.timing_monitor_function.function.function_arn,
            export_name="test-compliance-timing-monitor-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="compliance-scanner-function-name",
            value=self.compliance_scanner_function.function.function_name,
            export_name="test-compliance-scanner-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="compliance-timing-monitor-function-name",
            value=self.timing_monitor_function.function.function_name,
            export_name="test-compliance-timing-monitor-function-name" +
            "-" + environment
        )

        CfnOutput(
            scope=self,
            id="sns-dlq-"+environment,
            value=self.sns_topic.topic_arn,
            export_name='test-sns-dlq-'+environment
        )

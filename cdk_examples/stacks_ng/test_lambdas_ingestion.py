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

        self.invoice_file_movement_function = \
            DockerLambda(
                self,
                "ingestion-invoice-file-movement-function",
                environment=environment,
                ecr_name="test-ingestion-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Ingestion.Aws::test.Ingestion.Aws.InvoiceFileMovementFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        self.invoice_sets_function = \
            DockerLambda(
                self,
                "ingestion-invoice-sets-function",
                environment=environment,
                ecr_name="test-ingestion-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Ingestion.Aws::test.Ingestion.Aws.InvoiceSetsFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"],
                enable_dlq=True,
                sns_arn=alarm_sns_arn
            )

        self.jpm_cbm_function = \
            DockerLambda(
                self,
                "ingestion-jpm-cbm-function",
                environment=environment,
                ecr_name="test-ingestion-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Ingestion.Aws::test.Ingestion.Aws.JpmCbmFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        self.timing_monitor_function = \
            DockerLambda(
                self,
                "ingestion-timing-monitor-function",
                environment=environment,
                ecr_name="test-ingestion-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Ingestion.Aws::test.Ingestion.Aws.TimingMonitorFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        # Creating SQS for invoice-sets and setting up event for function
        self.invoice_sets_queue = SQSQueue(
            self,
            "ingestion-invoice-sets-queue",
            environment=environment,
            queue_name="invoice-sets",
            visibility_timeout=Duration.seconds(1800)
        )
        self.sqs_event_invoice_sets = SqsEventSource(
            self.invoice_sets_queue.queue
        )
        self.invoice_sets_function.function.add_event_source(
            self.sqs_event_invoice_sets
        )

        # Creating CW Scheduled Event Rules for Scheduled functions
        # For Invoice File Movement
        self.invoice_file_movement_rule = CWEventRuleCron(
            self,
            "invoice-file-movement-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["invoice_file_movement"]["enabled"],
            lambda_arn=self.invoice_file_movement_function.function.function_arn,  # noqa
            lambda_name=self.invoice_file_movement_function.function.function_name,  # noqa
            rate_time=metadata.get(
                "event_rules"
            )["invoice_file_movement"]["rate_limit"],
            rule_name="invoice-file-movement"+"-"+environment
        )
        # For JPM CBM
        self.jpm_cbm_rule = CWEventRuleCron(
            self,
            "jpm_cbm_rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["ingestion_jpm_cbm"]["enabled"],
            lambda_arn=self.jpm_cbm_function.function.function_arn,
            lambda_name=self.jpm_cbm_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["ingestion_jpm_cbm"]["rate_limit"],
            rule_name="ingestion_jpm_cbm"+"-"+environment
        )
        # For Timing Monitor
        self.timing_monitor_rule = CWEventRuleCron(
            self,
            "timing-monitor-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["timing_monitor"]["enabled"],
            lambda_arn=self.timing_monitor_function.function.function_arn,
            lambda_name=self.timing_monitor_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["timing_monitor"]["rate_limit"],
            rule_name="timing-monitor"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="ingestion-invoice-file-movement-function-arn",
            value=self.invoice_file_movement_function.function.function_arn,
            export_name="test-ingestion-invoice-file-movement-function-arn"
            + "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-invoice-sets-function-arn",
            value=self.invoice_sets_function.function.function_arn,
            export_name="test-ingestion-invoice-sets-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-jpm-cbm-function-arn",
            value=self.jpm_cbm_function.function.function_arn,
            export_name="test-ingestion-jpm-cbm-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-timing-monitor-function-arn",
            value=self.timing_monitor_function.function.function_arn,
            export_name="test-ingestion-timing-monitor-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-invoice-file-movement-function-name",
            value=self.invoice_file_movement_function.function.function_name,
            export_name="test-ingestion-invoice-file-movement-function-name"
            + "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-invoice-sets-function-name",
            value=self.invoice_sets_function.function.function_name,
            export_name="test-ingestion-invoice-sets-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-jpm-cbm-function-name",
            value=self.jpm_cbm_function.function.function_name,
            export_name="test-ingestion-jpm-cbm-function-name" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="ingestion-timing-monitor-function-name",
            value=self.timing_monitor_function.function.function_name,
            export_name="test-ingestion-timing-monitor-function-name" +
            "-" + environment
        )

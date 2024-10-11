from .modules.lambda_function import DockerLambda
from .modules.cloudwatch_event import CWEventRuleCron
from constructs import Construct
from aws_cdk import (
  Stack as stack,
  CfnOutput
)


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

        self.end_of_day_function = \
            DockerLambda(
                self,
                "reconciliation-end-of-day-function",
                environment=environment,
                ecr_name="test-reconciliation-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Reconciliation.Aws::test.Reconciliation.Aws.EndOfDayFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get(
                    "event_rules"
                )["reconciliation_end_of_day"]["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        # For EndOfDay Function
        self.end_of_day_rule = CWEventRuleCron(
            self,
            "reconciliation-end-of-day-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["reconciliation_end_of_day"]["enabled"],
            lambda_arn=self.end_of_day_function.function.function_arn,
            lambda_name=self.end_of_day_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["reconciliation_end_of_day"]["rate_limit"],
            rule_name="end_of_day_function"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="reconciliation-end-of-day-function-arn",
            value=self.end_of_day_function.function.function_arn,
            export_name="test-reconciliation-end-of-day-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="reconciliation-end-of-day-function-name",
            value=self.end_of_day_function.function.function_name,
            export_name="test-reconciliation-end-of-day-function-name" +
            "-" + environment
        )

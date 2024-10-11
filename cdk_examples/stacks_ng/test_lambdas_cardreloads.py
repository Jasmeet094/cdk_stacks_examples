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

        self.cardreloads_function = \
            DockerLambda(
                self,
                "cardreloads-function",
                environment=environment,
                ecr_name="test-cardreloads-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.CardReloads.Aws::test.CardReloads.Aws.CardReloadTimingMonitorFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        self.cardreloads_function_rule = CWEventRuleCron(
            self,
            "cardreloads-function-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["timing_monitor"]["enabled"],
            lambda_arn=self.cardreloads_function.function.function_arn,
            lambda_name=self.cardreloads_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["timing_monitor"]["rate_limit"],
            rule_name="cardreloads-function-rule"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="cardreloads-function-arn",
            value=self.cardreloads_function.function.function_arn,
            export_name="test-cardreloads-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="cardreloads-function-name",
            value=self.cardreloads_function.function.function_name,
            export_name="test-cardreloads-function-name" +
            "-" + environment
        )

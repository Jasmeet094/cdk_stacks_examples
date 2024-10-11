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

        self.enrichment_function = \
            DockerLambda(
                self,
                "enrichment-function",
                environment=environment,
                ecr_name="test-enrichment-aws",
                vpc_id=metadata.get("vpc_id"),
                account_id=metadata.get("id"),
                region=metadata.get("region"),
                cmd=["test.Enrichment.Aws::test.Enrichment.Aws.EnrichmentFunction::Execute"],  # noqa
                application_secrets="test_ng_services_api",
                environment_variables={
                    "ENV": environment
                },
                timeout=metadata.get("lambdas")["timeout"],
                memory_size=metadata.get("lambdas")["memory_size"]
            )

        self.enrichment_function_rule = CWEventRuleCron(
            self,
            "enrichment-function-rule",
            environment=environment,
            enabled=metadata.get(
                "event_rules"
            )["enrichment"]["enabled"],
            lambda_arn=self.enrichment_function.function.function_arn,
            lambda_name=self.enrichment_function.function.function_name,
            rate_time=metadata.get(
                "event_rules"
            )["enrichment"]["rate_limit"],
            rule_name="enrichment-function-rule"+"-"+environment
        )

        CfnOutput(
            scope=self,
            id="enrichment-function-arn",
            value=self.enrichment_function.function.function_arn,
            export_name="test-enrichment-function-arn" +
            "-" + environment
        )
        CfnOutput(
            scope=self,
            id="enrichment-function-name",
            value=self.enrichment_function.function.function_name,
            export_name="test-enrichment-function-name" +
            "-" + environment
        )

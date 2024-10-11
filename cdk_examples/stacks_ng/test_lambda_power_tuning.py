from constructs import Construct
from aws_cdk import (
    Stack as stack,
    aws_sam
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

        aws_sam.CfnApplication(
            self,
            construct_id+"-"+environment,
            location=aws_sam.CfnApplication.ApplicationLocationProperty(
                application_id=metadata.get("lambda_power_tuning")["application_id"],  # noqa
                semantic_version=metadata.get("lambda_power_tuning")["semantic_version"]  # noqa
            ),
            parameters={
                "lambdaResource": metadata.get("lambda_power_tuning")["lambda_resource"],  # noqa
                "PowerValues": metadata.get("lambda_power_tuning")["power_values"]  # noqa
            }
        )

from .base.s3 import S3Bucket
from constructs import Construct
from aws_cdk import (
    Stack as stack
)


class Stack(stack):

    def bucket_environment(self, environment):
        if environment == "test-dev":
            return "test-develop"
        elif environment == "test-prod":
            return "test-production"
        else:
            return environment

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # S3 bucket for fx-ng project CICD
        S3Bucket(
            scope=self,
            bucket_name="test-ng-db-queries-data",
            environment=self.bucket_environment(environment)
        )

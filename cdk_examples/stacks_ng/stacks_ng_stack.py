from aws_cdk import (
    Duration,
    Stack,
    aws_sqs as sqs,
)
from constructs import Construct


# A sample stack to show how to unit test CDK
class StacksNgStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # example resource
        sqs.Queue(
             self, "StacksNgQueue",
             visibility_timeout=Duration.seconds(300),
        )

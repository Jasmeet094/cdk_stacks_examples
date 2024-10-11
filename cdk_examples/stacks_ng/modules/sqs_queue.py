from aws_cdk import (
    aws_sqs as sqs
)


class SQSQueue:

    def __init__(
            self,
            scope,
            id,
            environment,
            queue_name,
            visibility_timeout,
            **kwargs):

        self.queue = sqs.Queue(
            scope,
            id=id + "-" + environment,
            queue_name=queue_name,
            visibility_timeout=visibility_timeout
        )

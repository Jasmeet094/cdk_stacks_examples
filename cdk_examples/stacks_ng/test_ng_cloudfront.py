from aws_cdk import (
    Stack as stack,
)
from .modules.cloudfront import CloudFront
from .base.s3 import S3Bucket
from constructs import Construct


class Stack(stack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, id, **kwargs)

        # S3 bucket for static content
        bucket_name = "test-platform-static-files-bucket"
        S3Bucket(
            scope=self,
            bucket_name=bucket_name,
            environment=environment
        )

        # Cloudfront distribution for the static content bucket
        self.cloudfront_platform = CloudFront(
            self,
            "test-platform-cloudfront",
            environment,
            metadata,
            bucket_name+"-"+environment,
            metadata.get("region"),
            metadata.get("cloudfront")["platform_cname"],
            metadata.get("certificates")[0],
            metadata.get("cloudfront")["default_root_object"],
            **kwargs
        )

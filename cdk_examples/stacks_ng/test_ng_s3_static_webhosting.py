from .base.s3 import StaticWebsiteHosting
from aws_cdk import (
    Stack as stack,
    aws_s3 as s3,
    aws_route53 as route53,
    aws_route53_targets as targets
)

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

        domain_name = metadata.get("hostedZone")
        static_website_buckets = metadata.get("static_website_buckets")

        for bucket in static_website_buckets:
            bucket_name = bucket.get("bucket_name", "")
            host_name = bucket.get("host_name", "")

            StaticWebsiteHosting(
                scope=self,
                bucket_name=bucket_name,
                host_name=host_name
            )

            route53.ARecord(
                self,
                id="ARecord-"+bucket_name+"-"+environment,
                record_name=bucket_name,
                target=route53.RecordTarget(
                    alias_target=targets.BucketWebsiteTarget(
                        bucket=s3.Bucket.from_bucket_name(
                            self,
                            id="Arecord-target-"+bucket_name,
                            bucket_name=bucket_name
                        )
                    )
                ),
                zone=route53.HostedZone.from_lookup(
                    self,
                    id=domain_name+"-"+bucket_name,
                    domain_name=domain_name
                )
            )

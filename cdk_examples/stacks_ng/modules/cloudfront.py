import aws_cdk as cdk
from aws_cdk.aws_cloudfront import (
    CfnDistribution,
    CfnCloudFrontOriginAccessIdentity
)


class CloudFront:

    def __init__(
        self,
        scope,
        id,
        environment,
        metadata,
        bucket_name,
        region=None,
        aliases=None,
        acm_arn=None,
        root_object=None,
        **kwargs
    ):

        cfn_cloud_front_origin_access_identity = CfnCloudFrontOriginAccessIdentity(   # noqa
            scope,
            id=id+str(region),
            cloud_front_origin_access_identity_config=CfnCloudFrontOriginAccessIdentity.CloudFrontOriginAccessIdentityConfigProperty( # noqa
                    comment="Origin-Access-Identity"+"-"+str(bucket_name)+"-"+str(region)  # noqa
            )
        )

        CfnDistribution(
            scope,
            id+"-"+str(bucket_name)+"-"+str(region),
            distribution_config=CfnDistribution.DistributionConfigProperty( # noqa
                enabled=True,
                aliases=[aliases],
                default_root_object=root_object,
                viewer_certificate=CfnDistribution.ViewerCertificateProperty(
                    acm_certificate_arn=acm_arn,
                    minimum_protocol_version="TLSv1.2_2021",
                    ssl_support_method="sni-only"
                ),
                origins=[CfnDistribution.OriginProperty(
                    domain_name=str(bucket_name)+".s3."+str(region)+".amazonaws.com", # noqa
                    id=str(bucket_name)+".s3."+str(region)+".amazonaws.com",
                    s3_origin_config = CfnDistribution.S3OriginConfigProperty( # noqa
                        origin_access_identity=cdk.Fn.join(
                            "",
                            [
                                "origin-access-identity/cloudfront/",
                                cfn_cloud_front_origin_access_identity.ref
                            ]
                        )
                    )
                )],
                price_class="PriceClass_100",
                default_cache_behavior=CfnDistribution.DefaultCacheBehaviorProperty(  # noqa
                    target_origin_id=str(bucket_name)+".s3."+str(region)+".amazonaws.com", # noqa
                    viewer_protocol_policy="allow-all",
                    forwarded_values=CfnDistribution.ForwardedValuesProperty(
                        query_string=True
                    )
                )
            )
        )

        cdk.CfnOutput(
           scope,
           "oai-id-"+environment+"-"+id,
           value=cfn_cloud_front_origin_access_identity.ref,
           export_name="oai-id-"+environment+"-"+id
        )

from aws_cdk import (
    aws_iam as iam,
    aws_lambda as lambda_,
    custom_resources as cr,
    CustomResource,
    Duration)


class AliasRecord:
    def __init__(self, scope, id, elb, weight, identifier,
                 dns_record=None, hosted_zone_id=None, **kwargs):

        self.record = CustomResource(
            scope,
            "cr-record"+id,
            service_token=kwargs.get("provider").service_token,
            properties={
                "HOSTED_ZONE": (hosted_zone_id if hosted_zone_id else
                                kwargs.get("metadata").get("hostedZoneId")),
                "RECORD_NAME": dns_record,
                "RECORD_TYPE": "A",
                "TARGET": elb.load_balancer_dns_name,
                "TARGET_ZONE": elb.load_balancer_canonical_hosted_zone_id,
                "WEIGHT": weight if weight is not None else "-1",
                "SET_IDENTIFIER": (identifier if identifier is not None
                                   else "-1")
            })


class CNameRecord:
    def __init__(self, scope, id, env, target, weight,
                 identifier, metadata, **kwargs):

        self.record = None

        record_name = id+"."+metadata.get("hostedZone")
        self.record = CustomResource(
            scope,
            "cr-record"+id,
            service_token=kwargs.get("provider").service_token,
            properties={
                "HOSTED_ZONE": metadata.get("hostedZoneId"),
                "RECORD_NAME": record_name,
                "RECORD_TYPE": "CNAME",
                "TARGET": target,
                "WEIGHT": weight if weight is not None else "-1",
                "SET_IDENTIFIER": (identifier if identifier is not None
                                   else "-1")
            })


class Route53Function:
    def __init__(self, scope, id, metadata: dict, **kwargs):
        self.function = lambda_.Function(
            scope,
            "lambda-"+id,
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset(
                "assets/r53-function"),
            handler="main.handler",
            environment={
                "CROSS_ACCOUNT_ROLE": metadata.get("route53Role")
            },
            initial_policy=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[metadata.get("route53Role")]
                )
            ])

        self.provider = cr.Provider(scope,
                                    "route53Provider"+id,
                                    on_event_handler=self.function)


class CNameRecordVerificationFunction:
    def __init__(self, scope, id, metadata: dict, timeout=15, **kwargs):
        self.function = lambda_.Function(
            scope,
            "lambda-" + id,
            runtime=lambda_.Runtime.PYTHON_3_11,
            timeout=Duration.seconds(timeout),
            code=lambda_.Code.from_asset(
                "assets/cname-validation"),
            handler="main.handler",
            environment={
                "CROSS_ACCOUNT_ROLE": metadata.get("route53Role")
            },
            initial_policy=[
                iam.PolicyStatement(
                    actions=[
                        "sts:AssumeRole",
                        "acm:*"
                    ],
                    resources=["*"]
                )
            ])

        self.provider = cr.Provider(scope,
                                    "cnameVerifyProvider" + id,
                                    on_event_handler=self.function)


class CNameRecordVerification:
    def __init__(self, scope, id, tag, provider, hosted_zone):

        self.record = CustomResource(
            scope,
            "cr-record"+id,
            service_token=provider.service_token,
            properties={
                "TAG": tag,
                "HOSTED_ZONE": hosted_zone,
                "RECORD_TYPE": "CNAME"
            })

from constructs import Construct
from aws_cdk import Stack
from aws_cdk import (
    aws_elasticloadbalancingv2 as elbv2,
)
from .base.route53 import AliasRecord, Route53Function


class testAlb(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, construct_id, **kwargs)

        test_app_alb_arn = metadata.get('test_app')['alb_arn']
        test_app_alb = elbv2.ApplicationLoadBalancer.from_lookup(
            self,
            'idAlb'+construct_id,
            load_balancer_arn=test_app_alb_arn
        )

        # Route53 custom resource in master account
        route53_function = Route53Function(self,
                                           id='route53Function'+construct_id,
                                           metadata=metadata)

        # Create wildcard DNS Record
        AliasRecord(self,
                    "aRecord"+construct_id+"-"+environment,
                    test_app_alb,
                    "-1",
                    "-1",
                    dns_record=f"*.{metadata.get('hostedZone')}",
                    provider=route53_function.provider,
                    metadata=metadata)

        # Create listener rule for the wildcard DNS record
        portal_target_group = elbv2.ApplicationTargetGroup.\
            from_target_group_attributes(
                self,
                "portal-tg-"+construct_id,
                target_group_arn=(metadata.get('test_app')
                                  ["target_group"])
            )
        listener_https = elbv2.ApplicationListener.from_lookup(
            self,
            "AlbHttpsListenerRule"+construct_id,
            load_balancer_arn=test_app_alb_arn,
            listener_port=443,
        )
        # Prod portal wildcard domain listener rule
        elbv2.ApplicationListenerRule(
            self,
            "listener-rule" + construct_id + "-" + environment,
            listener=listener_https,
            priority=10000,
            action=elbv2.ListenerAction.forward(
                target_groups=[portal_target_group]),
            conditions=[
                elbv2.ListenerCondition.host_headers(
                    [f"*.{metadata.get('hostedZone')}"])
            ])

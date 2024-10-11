from aws_cdk import (
    aws_sns as sns,
    aws_ec2 as ec2,
    aws_ecs as ecs
)
from aws_cdk.aws_events import CfnRule
import json
from constructs import Construct
from aws_cdk import Stack, Fn


class FargateSpotNotification(Stack):
    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        vpc_id = metadata.get("vpc_id")
        self.vpc = ec2.Vpc.from_lookup(
            self,
            "vpc-id-"+environment,
            vpc_id=vpc_id
        )

        ecs_service_sg_id = Fn.import_value(
            "ng-ecs-services-security-group-"+environment
        )
        self.service_security_group = ec2.SecurityGroup.from_security_group_id(  # noqa
            self,
            "sg-id-fargate-service-"+environment,
            security_group_id=ecs_service_sg_id
        )

        # Import and Find existing ECS Cluster
        ecs_cluster_name = Fn.import_value(
            "ng-ecs-cluster-name-"+environment
        )
        self.cluster = ecs.Cluster.from_cluster_attributes(
            self,
            "cluster-id-"+environment,
            cluster_name=ecs_cluster_name,
            security_groups=[self.service_security_group],
            vpc=self.vpc
        )

        sns_subscription = []
        for endpoint in metadata.get("capacity_provider_strategy")[
                "email_sns_endpoint"]:
            sns_subscription.append(sns.CfnTopic.SubscriptionProperty(
                protocol="email",
                endpoint=endpoint
            ))

        sns_topic = sns.CfnTopic(
            self,
            id=construct_id+"-FargateSpot-status-"+environment,
            display_name=construct_id+"-FargateSpot-status-"+environment,
            fifo_topic=False,
            subscription=sns_subscription
        )
        cluster_arn = "arn:aws:ecs:" + \
            str(metadata.get("region"))+":" + \
            str(metadata.get(id))+":cluster/"+str(
                self.cluster.cluster_name)
        self.ecs_cluster_arn = Fn.import_value(
            "ecs-cluster-arn" + "-" + environment)
        self.event_pattern = '''
        {
            "source": ["aws.ecs"],
            "detail-type": ["ECS Task State Change"],
            "detail": {
                "clusterArn": ["TO_REPLACE"],
                "stoppedReason": ["Your Spot Task was interrupted."],
                "stopCode": ["TerminationNotice"]
            }
        }'''.replace('TO_REPLACE', cluster_arn)

        CfnRule(
            self,
            id=construct_id+"-sns-"+environment,
            name=construct_id+"-sns-"+environment,
            event_pattern=json.loads(self.event_pattern),
            targets=[
                CfnRule.TargetProperty(
                    id=construct_id+"-target-SNS-"+environment,
                    arn=sns_topic.ref
                )
            ]
        )

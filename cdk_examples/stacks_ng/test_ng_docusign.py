from .base.ecs import ECSService
from .base.alb import ApplicationLoadBalancer
from constructs import Construct
from aws_cdk import (
    custom_resources as cr,
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_iam as iam,
    aws_lambda as lambda_,
    Stack as stack,
    Tags,
    Fn
)
import aws_cdk.aws_ssm as ssm


class Stack(stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)
        self.scope = scope
        self.construct_id = construct_id

        # Import and Find ECS execution role
        ecs_exe_role_arn = Fn.import_value('ng-ecs-task-exe-role-arn')
        ecs_exe_role = iam.Role.from_role_arn(self,
                                              id="ng-ecs-task-exe-role",
                                              role_arn=ecs_exe_role_arn)

        # Import and Find existing VPC
        vpc_id = metadata.get("vpc_id")
        self.vpc = ec2.Vpc.from_lookup(
            self,
            "vpc-id-"+environment,
            vpc_id=vpc_id
        )

        # Import and Find Existing Security Group for ECS Service
        ecs_service_sg_id = Fn.import_value(
            "ng-ecs-services-security-group-"+environment
        )
        self.service_security_group = ec2.SecurityGroup.from_security_group_id(
            self,
            "ng-sg-id-fargate-service-"+environment,
            security_group_id=ecs_service_sg_id
        )

        # Import and Find existing ECS Cluster
        ecs_cluster_name = Fn.import_value(
            "ng-ecs-cluster-name-"+environment
        )
        self.cluster = ecs.Cluster.from_cluster_attributes(
            self,
            "ng-cluster-id-"+environment,
            cluster_name=ecs_cluster_name,
            security_groups=[self.service_security_group],
            vpc=self.vpc
        )

        # Create a new ALB for the new stack
        self.load_balancer = ApplicationLoadBalancer(
            self,
            construct_id,
            environment,
            self.vpc,
            metadata,
            public=True
        )

        # Tag load balancer with the ecs service name
        Tags.of(self.load_balancer.alb).add(
            "Applications",
            f"test-ng-docusign-{environment}" # noqa
        )

        # Create a new Route53 provider for the new stack
        self.route53_provider_function = cr.Provider(
            self,
            "route53Provider-Fargate",
            on_event_handler=self.get_route53_function(
                construct_id,
                metadata
            ))

        # ECS Services
        self.test_ng_admin_portal = self.create_test_ng_docusign_portal(
            metadata, environment, ecs_exe_role
        )

    def get_route53_function(self, construct_id, metadata):
        return lambda_.Function(
            self,
            "ng-lambda-fargate-" + construct_id,
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

    def create_test_ng_docusign_portal(
        self,
        metadata,
        environment,
        execution_role
    ):

        # Secrets
        secret_vars = {}

        # Environment variables
        env_vars = {}

        # DNS name for test-docusign-api
        dns_name = "docusign"

        # latest image version id
        commit_id = ssm.StringParameter.value_for_string_parameter(
            self, "test-ng-docusign-commit-id")

        # ECS Service for test-docusign-api
        return ECSService(
            self,
            "test-ng-docusign",
            metadata.get("test_ng_docusign_portal")["image"] + ":" + commit_id,  # noqa
            cluster=self.cluster,
            vpc=self.vpc,
            load_balancer=self.load_balancer,
            service_security_group=self.service_security_group,
            assign_public_ip=True,
            environment=environment,
            secrets=secret_vars,
            priority=20,
            container_port=443,
            memory_limit_mib=metadata.get("test_ng_docusign_portal")[
                "memory_limit_mib"],
            cpu=metadata.get("test_ng_docusign_portal")["cpu"],
            env_vars=env_vars,
            task_role=execution_role,
            execution_role=execution_role,
            metadata=metadata,
            dns_id=[dns_name],
            enable_circuit_breaker=True,
            portal=True
        )

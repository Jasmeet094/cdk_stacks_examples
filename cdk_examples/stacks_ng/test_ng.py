from .base.base import testStack
from .base.iam import ECSExecutionRole
from .base.ecs import ECSService
from .base.s3 import SecureBucket
from .modules.environment import EnvVariables
from aws_cdk import (
    aws_ecs as ecs,
    Tags,
    aws_secretsmanager as sm
)
from constructs import Construct
import aws_cdk.aws_ssm as ssm


class Stack(testStack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, construct_id, metadata, environment, **kwargs)

        ecs_exe_role_name = "test_ng_execution_role"

        self.Role = ECSExecutionRole(
            self,
            ecs_exe_role_name,
            environment
        )

        self.construct_id = construct_id

        # Tag load balancer with the ECS ervice name
        Tags.of(self.load_balancer.alb).add(
            "Applications",
            f"test-ng-api-{environment} test-ng-notificaton-api-{environment}" # noqa
        )

        self.next_gen_bucket = SecureBucket(self,
                                            environment+"-ng",
                                            normalize_bucket_name=True)

        self.test_ng_api = self.create_test_ng_api(
            metadata, environment, self.Role.role)

        self.test_ng_notifications_api = \
            self.create_test_ng_notifications_api(
                metadata, environment, self.Role.role
            )

    def create_test_ng_api(
            self,
            metadata,
            environment,
            execution_role
    ):
        # Secrets
        secret_vars = {}
        secret = sm.Secret.from_secret_name_v2(
            self,
            "test-ng-api-secret",
            metadata.get("test_ng_api")["SECRET_NAME"])
        for key in EnvVariables.test_ng_api:
            secret_vars[key] = ecs.Secret.from_secrets_manager(
                secret, key)

        # Environment variables
        env_vars = {}

        # latest image version id
        commit_id = ssm.StringParameter.value_for_string_parameter(
            self, "test-ng-api-commit-id")

        # ECS Service for test-nextgen-api
        return ECSService(
            self,
            "test-ng-api",
            metadata.get("test_ng_api")["image"] + ":" + commit_id,
            self.cluster.cluster,
            self.network.vpc,
            self.load_balancer,
            self.network.ApiServiceSecurityGroup,
            assign_public_ip=True,
            environment=environment,
            secrets=secret_vars,
            priority=10,
            container_port=443,
            memory_limit_mib=metadata.get("test_ng_api")[
                "memory_limit_mib"],
            cpu=metadata.get("test_ng_api")["cpu"],
            env_vars=env_vars,
            task_role=execution_role,
            execution_role=execution_role,
            metadata=metadata,
            dns_id=["developer", "client-api", "api"],
            enable_circuit_breaker=True
        )

    def create_test_ng_notifications_api(
            self,
            metadata,
            environment,
            execution_role
    ):
        # Secrets
        secret_vars = {}
        secret = sm.Secret.from_secret_name_v2(
            self,
            "test-ng-notifications-api-secret",
            metadata.get("test_ng_notifications_api")["SECRET_NAME"])
        for key in EnvVariables.test_ng_notifications_api:
            secret_vars[key] = ecs.Secret.from_secrets_manager(
                secret, key)

        # Environment variables
        env_vars = {}

        # latest image version id
        commit_id = ssm.StringParameter.value_for_string_parameter(
            self, "test-ng-notifications-commit-id")

        # ECS Service for test-nextgen-api
        return ECSService(
            self,
            "test-ng-notifications-api",
            metadata.get("test_ng_notifications_api")[
                "image"] + ":" + commit_id,
            self.cluster.cluster,
            self.network.vpc,
            self.load_balancer,
            self.network.ApiServiceSecurityGroup,
            assign_public_ip=True,
            environment=environment,
            secrets=secret_vars,
            priority=20,
            container_port=443,
            memory_limit_mib=metadata.get("test_ng_notifications_api")[
                "memory_limit_mib"],
            cpu=metadata.get("test_ng_notifications_api")["cpu"],
            env_vars=env_vars,
            task_role=execution_role,
            execution_role=execution_role,
            metadata=metadata,
            dns_id=["webhook-api"],
            enable_circuit_breaker=True
        )

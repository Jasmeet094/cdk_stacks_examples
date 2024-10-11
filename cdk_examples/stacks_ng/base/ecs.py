from .route53 import AliasRecord
from aws_cdk import (
    aws_ec2 as ec2,
    aws_ecs as ecs,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
    aws_secretsmanager as secretsmanager,
    RemovalPolicy,
    CfnOutput,
    Duration,
    NestedStack
)


class ECSCluster:

    def __init__(self, scope, id, environment, vpc, **kwargs):

        self.cluster = ecs.Cluster(
            scope,
            "cluster-" + id + "-" + environment,
            vpc=vpc,
            enable_fargate_capacity_providers=(
                True
                if environment != "test-prod" and environment != "test-stage"  # noqa
                else None)
        )

        CfnOutput(
            scope=scope,
            id="ecs_cluster_name",
            value=str(self.cluster.cluster_name),
            export_name="ng-ecs-cluster-name" + "-" + environment
        )


class ECSService:

    def __init__(self, scope, id, image, cluster, vpc, load_balancer,
                 service_security_group, assign_public_ip,
                 environment, **kwargs):

        self.scope = scope
        self.nested_stack = NestedStack(scope, id)
        self.assign_public_ip = assign_public_ip
        metadata = kwargs.get("metadata")

        self.task_definition = ecs.FargateTaskDefinition(
            self.nested_stack,
            "task-" + id + "-" + environment,
            cpu=kwargs.get("cpu", 512),
            memory_limit_mib=kwargs.get("memory_limit_mib", 2048),
            task_role=kwargs.get("task_role"),
            execution_role=kwargs.get("execution_role")
        )

        dd_secret = secretsmanager.Secret.from_secret_name_v2(
            self.nested_stack,
            "dd-secret",
            "stacks_dd_key")

        self.log_driver = ecs.FireLensLogDriver(
            options={
            }
        )

        environment_variables = {
            **kwargs.get("env_vars", {}),
            "DD_SERVICE": environment + "-" + id,
            "ASPNETCORE_URLS": "https://+:443",
            "DeploymentEnvironment": environment.split("-")[1]
        }
        self.container_definition = self.task_definition.add_container(
            "container-" + id + "-" + environment,
            image=ecs.ContainerImage.from_registry(image),
            environment=environment_variables,
            secrets=kwargs.get("secrets", {}),
            logging=self.log_driver,
            essential=True
        )

        self.container_port_mappings = ecs.PortMapping(
            container_port=kwargs.get("container_port", 80),
            protocol=ecs.Protocol.TCP
        )

        self.container_definition.add_port_mappings(
            self.container_port_mappings)

        self.container_definition.add_ulimits(ecs.Ulimit(
            name=ecs.UlimitName.NOFILE,
            hard_limit=65536,
            soft_limit=65536
        ))

        self.log_group = logs.LogGroup(
            scope,
            id + "-" + "task-definition" + "-" + environment,
            log_group_name=id + "-" + "task-definition" + "-" + environment
        )

        self.aws_log_driver = ecs.LogDriver.aws_logs(
            stream_prefix=(
                environment
                + "/"
                + self.container_definition.container_name),
            log_group=logs.LogGroup.from_log_group_arn(
                scope,
                id + "-" + "ILogGroup" + "-" + environment,
                self.log_group.log_group_arn
            )
        )

        self.task_definition.add_firelens_log_router(
            "logrouter-" + id + "-" + environment,
            image=ecs.ContainerImage.from_registry(
                "330157172028.dkr.ecr.us-east-1.amazonaws.com/fluent-bit-firelens"),  # noqa
            environment={
                "DD_API_KEY": dd_secret.secret_value_from_json(
                    "DD_API_KEY").to_string(),
                "ENVIRONMENT": environment,
                "ID": id,
                "REGION": metadata.get("region")
            },
            essential=True,
            memory_reservation_mib=50,
            firelens_config=ecs.FirelensConfig(
                type=ecs.FirelensLogRouterType.FLUENTBIT,
                options=ecs.FirelensOptions(
                    enable_ecs_log_metadata=True,
                    config_file_value="/extra.conf",
                    config_file_type=ecs.FirelensConfigFileType.FILE
                )
            ),
            logging=self.aws_log_driver
        )

        self.container_definition = self.task_definition.add_container(
            "datadog-agent-" + id + "-" + environment,
            image=ecs.ContainerImage.from_registry("datadog/agent:7.32.1"),
            environment={
                "DD_APM_ENABLED": "true",
                "DD_APM_ENV": environment,
                "ECS_FARGATE": "true",
                "DD_ANALYTICS_ENABLED": "true",
                "DD_API_KEY": dd_secret.secret_value_from_json(
                    "DD_API_KEY").to_string()
            },
            essential=True
        )

        self.container_definition.add_port_mappings(
            ecs.PortMapping(
                container_port=8126,
                protocol=ecs.Protocol.TCP
            )
        )

        if kwargs.get("desired_count") is not None:
            desired_count = kwargs.get("desired_count")
        else:
            desired_count = metadata.get("ecs_config")["desired_count"]

        self.service = ecs.FargateService(
            self.nested_stack,
            "svc-" + id + "-" + environment,
            service_name=id + "-" + environment,
            task_definition=self.task_definition,
            cluster=cluster,
            capacity_provider_strategies=([ecs.CapacityProviderStrategy(
                capacity_provider=metadata.get("capacity_provider_strategy")
                ["capacity_provider"],
                weight=metadata.get("capacity_provider_strategy")["weight"]
            )]
                if environment != "test-prod" and environment != "test-stage"  # noqa
                else None
            ),
            desired_count=desired_count,
            assign_public_ip=self.assign_public_ip,
            health_check_grace_period=(
                None if kwargs.get("worker", False)
                else kwargs.get(
                    "health_check_grace_period", Duration.seconds(300))
            ),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
                if self.assign_public_ip == False # noqa
                else ec2.SubnetType.PUBLIC
            ),
            security_groups=[service_security_group],
            platform_version=ecs.FargatePlatformVersion.VERSION1_4,
            circuit_breaker=(
                None if not kwargs.get('enable_circuit_breaker', False)
                else ecs.DeploymentCircuitBreaker(rollback=True)
            )
        )

        # Setup AutoScaling policy
        scaling = self.service.auto_scale_task_count(
            max_capacity=10,
            min_capacity=desired_count
        )
        if id == "test-ng-admin":
            scaling.scale_on_memory_utilization(
                "MemoryAutoScaling",
                target_utilization_percent=75,
                scale_in_cooldown=Duration.seconds(60),
                scale_out_cooldown=Duration.seconds(60),
            )
        else:
            scaling.scale_on_cpu_utilization(
                "CpuAutoScaling",
                target_utilization_percent=75,
                scale_in_cooldown=Duration.seconds(60),
                scale_out_cooldown=Duration.seconds(60),
            )

            scaling.scale_on_memory_utilization(
                "MemoryAutoScaling",
                target_utilization_percent=75,
                scale_in_cooldown=Duration.seconds(60),
                scale_out_cooldown=Duration.seconds(60),
            )

        self.cfn_service = self.service.node.children[0]
        self.cfn_service.add_override(
            "Properties.EnableExecuteCommand",
            True
        )

        worker = kwargs.get("worker", False)
        portal = kwargs.get("portal", False)

        if not worker:
            health_check_path = "/healthz"
            if portal:
                health_check_path = "/"
            self.health_check = elbv2.HealthCheck(
                interval=Duration.seconds(30),
                timeout=Duration.seconds(10),
                healthy_threshold_count=2,
                unhealthy_threshold_count=2,
                protocol=elbv2.Protocol.HTTPS if kwargs.get("container_port", 443) == 443 else elbv2.Protocol.HTTP, # noqa
                healthy_http_codes="200-399",
                path=health_check_path)

            # Attach ALB to ECS Service
            self.target_group = elbv2.ApplicationTargetGroup(
                self.nested_stack,
                "tg-" + id + "-" + environment,
                port=kwargs.get("container_port", 443),
                targets=[self.service],
                health_check=self.health_check,
                protocol=elbv2.ApplicationProtocol.HTTPS if kwargs.get("container_port", 443) == 443 else elbv2.ApplicationProtocol.HTTP, # noqa
                vpc=vpc
            )

            host_rule = []

            if kwargs.get("dns_id"):
                service_id = kwargs.get("dns_id")
            else:
                service_id = [id]

            for i in service_id:
                dns_record = f'{i}.{metadata.get("hostedZone")}'
                host_rule.append(dns_record)

                self.record = AliasRecord(
                    self.nested_stack,
                    "Arecord" + i,
                    load_balancer.alb,
                    kwargs.get("weight"),
                    kwargs.get("identifier"),
                    dns_record,
                    provider=scope.route53_provider_function,
                    metadata=kwargs.get("metadata")
                )

            self.listener_rule = elbv2.ApplicationListenerRule(
                self.nested_stack,
                "listener-rule" + id + "-" + environment,
                listener=load_balancer.https_listener,
                priority=kwargs.get("priority"),
                action=elbv2.ListenerAction.forward(
                    target_groups=[self.target_group]),
                conditions=[
                    elbv2.ListenerCondition.host_headers(
                        host_rule)
                ])

        # Cloudwatch Log Group
        self.log_group = logs.LogGroup(
            scope,
            environment + "-" + id + "-cloudwatch",
            log_group_name=environment + "-" + id + "-cloudwatch")
        self.log_group.apply_removal_policy(RemovalPolicy.DESTROY)

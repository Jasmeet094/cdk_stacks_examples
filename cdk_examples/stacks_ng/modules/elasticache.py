import aws_cdk.aws_elasticache as elasticache


class Elasticache:

    def __init__(
            self,
            scope,
            id,
            environment,
            subnet_ids,
            security_group_id,
            **kwargs):

        self.param_group = elasticache.CfnParameterGroup(
            scope,
            "redis-parameter-group-"+id+"-"+environment,
            cache_parameter_group_family=kwargs.get(
                                        "cache_parameter_group_family",
                                        "redis5.0"),
            description="Elastic Cache Parameter Group"
        )

        self.subnet_group = elasticache.CfnSubnetGroup(
            scope,
            "redis-subnet-group-"+id+"-"+environment,
            description="Redis Subnet Group",
            subnet_ids=subnet_ids
        )

        self.redis_replication_group = elasticache.CfnReplicationGroup(
            scope, "redis-"+id+"-"+environment,
            replication_group_description="Redis Replication Group",
            at_rest_encryption_enabled=kwargs.get(
                    "at_rest_encryption_enabled",
                    True
                    ),
            automatic_failover_enabled=kwargs.get(
                "automatic_failover_enabled",
                False
                ),
            auto_minor_version_upgrade=kwargs.get(
                "auto_minor_version_upgrade",
                True
                ),
            cache_node_type=kwargs.get("cache_node_type", "cache.t3.micro"),
            cache_parameter_group_name=self.param_group.ref,
            cache_subnet_group_name=self.subnet_group.ref,
            engine=kwargs.get("engine", "redis"),
            engine_version=kwargs.get("engine_version", "5.0.5"),
            num_node_groups=kwargs.get("num_node_groups", 1),
            replicas_per_node_group=kwargs.get("replicas_per_node_group", 0),
            replication_group_id="redis-"+id+"-"+environment,
            security_group_ids=[security_group_id],
            snapshot_window=kwargs.get("snapshot_window", "02:00-03:00"),
            preferred_maintenance_window=kwargs.get(
                "preferred_maintenance_window", "sun:05:00-sun:06:00"),
            snapshot_retention_limit=kwargs.get("snapshot_retention_limit", 7)
        )
        self.elasticache_primary_endpoint = self\
            .redis_replication_group.attr_primary_end_point_address

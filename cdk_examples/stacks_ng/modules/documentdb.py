from aws_cdk import (
    aws_docdb as docdb,
    aws_ec2 as ec2
)


class DocumentDB():
    def __init__(
            self,
            scope,
            id,
            metadata,
            environment,
            vpc,
            security_group_id,
            engine_version,
            preferred_maintenance_window,
            instance_class,
            instance_size,
            number_of_instances,
            parameters,
            **kwargs):

        truncated_environment = environment.split("-")[1]

        param_group = docdb.ClusterParameterGroup(
            scope,
            "paramgroup-"+id+"-"+environment,
            db_cluster_parameter_group_name="paramgroup-"+id+"-"+environment,
            family="docdb4.0",
            parameters=parameters
        )

        docdb.DatabaseCluster(
            scope,
            "documentdb-"+id+"-"+environment,
            master_user=docdb.Login(
                username="docdb"+truncated_environment,
                exclude_characters="\"!'$%&(),/:;<=>?@[\]^_`{|}~", # noqa
                secret_name=environment+"/docdb/creds1"
            ),
            instance_type=ec2.InstanceType.of(
                ec2.InstanceClass[instance_class],
                ec2.InstanceSize[instance_size]
            ),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),
            vpc=vpc,
            db_cluster_name="documentdb-"+id+"-"+environment,
            engine_version=engine_version,
            instances=number_of_instances,
            preferred_maintenance_window=preferred_maintenance_window,
            security_group=security_group_id,
            parameter_group=param_group,
            export_audit_logs_to_cloud_watch=True,
            deletion_protection=True
        )

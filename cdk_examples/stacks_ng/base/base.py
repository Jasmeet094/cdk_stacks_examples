from .network import Network
from .ecs import ECSCluster
from .alb import ApplicationLoadBalancer
from ..modules.elasticache import Elasticache
from .s3 import Bucket, BucketEncryption
from ..modules.documentdb import DocumentDB
from aws_cdk import (
    aws_lambda as lambda_,
    custom_resources as cr,
    aws_iam as iam,
    Stack)
from constructs import Construct
from typing import Any, Dict


class testStack(Stack):

    def __init__(self, scope: Construct, construct_id: str,
                 metadata: Dict[str, Any],
                 environment: str = "default",
                 **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        self.setup_bundling_options()
        self.setup_network(construct_id, environment, metadata)

        if environment not in ["test-sandbox",
                               "test-demo",
                               "test-hotfix-dev"]:
            self.setup_elasticache(construct_id, environment, metadata)
            self.setup_docdb(construct_id, environment, metadata)

        self.setup_cluster(construct_id, environment)
        self.setup_load_balancers(construct_id, environment, metadata)
        self.setup_route53(construct_id, metadata)

    def setup_bundling_options(self):
        self.bundling_options = {
            "image": lambda_.Runtime.PYTHON_3_11.bundling_image,
            "command": ["bash", "-c", "pip install -r requirements.txt -t /asset-output && cp -r . /asset-output"]  # noqa
        }

    def setup_network(self, construct_id: str, environment: str,
                      metadata: Dict[str, Any]):
        self.network = Network(self, construct_id, environment,
                               metadata.get("cidr"), metadata)

    def setup_elasticache(self, construct_id: str, environment: str,
                          metadata: Dict[str, Any]):
        elasticache_options = metadata.get("elasticache")
        self.elasticache = Elasticache(self, construct_id, environment,
                                       self.network.private_subnet_ids,
                                       self.network.elasticacheSecurityGroup,
                                       **elasticache_options)

    def setup_docdb(self, construct_id: str, environment: str,
                    metadata: Dict[str, Any]):
        self.docdb = DocumentDB(
            self,
            construct_id,
            metadata,
            environment,
            self.network.vpc,
            self.network.DocumentdbSecurityGroup,
            metadata.get("documentdb")["engine_version"],
            metadata.get("documentdb")["maintenance_window"],
            metadata.get("documentdb")["instance_type"]["instance_class"],
            metadata.get("documentdb")["instance_type"]["instance_size"],
            metadata.get("documentdb")["number_of_instances"],
            metadata.get("documentdb")["parameters"]
        )

    def setup_cluster(self, construct_id: str, environment: str):
        self.cluster = ECSCluster(self, construct_id,
                                  environment, self.network.vpc)

    def setup_load_balancers(self, construct_id: str, environment: str,
                             metadata: Dict[str, Any]):
        self.load_balancer = ApplicationLoadBalancer(self, construct_id,
                                                     environment,
                                                     self.network.vpc,
                                                     metadata,
                                                     public=True)
        self.private_load_balancer = ApplicationLoadBalancer(self,
                                                             construct_id + "private",  # noqa
                                                             environment,
                                                             self.network.vpc,
                                                             metadata,
                                                             public=False)
        self.setup_bucket_logs(environment)

    def setup_bucket_logs(self, environment: str):
        encryption = BucketEncryption.S3_MANAGED
        access_log_bucket = Bucket(self, id=f"{environment}-access-logs", encryption=encryption)  # noqa
        self.load_balancer.alb.log_access_logs(access_log_bucket)

        if environment == "test-prod":
            access_log_bucket_private = Bucket(self, id=f"{environment}-access-logs-private",  # noqa
                                               encryption=encryption)
            self.private_load_balancer.alb.log_access_logs(access_log_bucket_private)  # noqa

    def setup_route53(self, construct_id: str, metadata: Dict[str, Any]):
        route53_function = lambda_.Function(
            self, "lambda-" + construct_id,
            runtime=lambda_.Runtime.PYTHON_3_11,
            code=lambda_.Code.from_asset("assets/r53-function"),
            handler="main.handler",
            environment={"CROSS_ACCOUNT_ROLE": metadata.get("route53Role")},
            initial_policy=[
                iam.PolicyStatement(
                    actions=["sts:AssumeRole"],
                    resources=[metadata.get("route53Role")]
                )
            ]
        )

        self.route53_provider_function = cr.Provider(self, "route53Provider", on_event_handler=route53_function)  # noqa

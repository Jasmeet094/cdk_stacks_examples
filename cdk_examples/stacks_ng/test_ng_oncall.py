from constructs import Construct
from .modules.stop_services import stop
from .modules.resume_services import resume
import aws_cdk.aws_wafv2 as waf
from aws_cdk import (
  Stack as stack,
  CfnOutput
)


# These resources will be used by OnCall.
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

        self.stop_lambda = stop(
            self,
            "test-stop-all-services",
            metadata,
            environment=environment,
            rds_cluster_identifier=str(metadata.get(
              "stop_start_services")["rds_cluster"]),
            docdb_cluster_identifier=metadata.get(
                "stop_start_services")["docdb_cluster"]
        )

        self.resume_lambda = resume(
            self,
            "test-resume-all-services",
            metadata,
            environment=environment,
            rds_cluster_identifier=str(metadata.get(
              "stop_start_services")["rds_cluster"]),
            docdb_cluster_identifier=metadata.get(
                "stop_start_services")["docdb_cluster"]
        )

        # AWS WAF IP Sets
        ip_set = waf.CfnIPSet(
            self,
            id=construct_id+"-ipset",
            name="OnCallIPSet",
            addresses=metadata.get("oncall_addresses"),
            ip_address_version='IPV4',
            scope='REGIONAL'
            )

        CfnOutput(
                self,
                "oncall-ipset",
                value=ip_set.attr_arn,
                export_name='oncall-ip-set-arn'
            )

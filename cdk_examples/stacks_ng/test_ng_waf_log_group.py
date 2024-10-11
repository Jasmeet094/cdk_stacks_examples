from constructs import Construct
from aws_cdk import (
  Stack as stack,
  CfnOutput,
  aws_logs as logs
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

        self.waf_log_group = logs.CfnLogGroup(
            self,
            "aws-waf-logs-"+self.construct_id+"-"+environment,
            log_group_name="aws-waf-logs-"+self.construct_id+"-"+environment,
            retention_in_days=14
        )

        self.log_group_arn = "arn:aws:logs:"+metadata.get(
            "region")+":"+metadata.get("id")+":log-group:"+str(
                self.waf_log_group.log_group_name)

        CfnOutput(
            scope=self,
            id="waf_loggroup",
            value=self.log_group_arn,
            export_name="test-ng-waf-log-group-arn" + "-" + environment
        )

import aws_cdk.aws_lambda as lambda_
import aws_cdk.aws_iam as iam
import aws_cdk.aws_events as events
from aws_cdk import Duration


class stop:
    def __init__(
            self,
            scope,
            id,
            metadata,
            environment,
            rds_cluster_identifier,
            docdb_cluster_identifier,
            **kwargs):
        # Lambda function
        self.lambda_function = lambda_.Function(
            scope,
            id + "-" + environment,
            function_name=id + "-" + environment,
            runtime=lambda_.Runtime.PYTHON_3_11,
            timeout=Duration.seconds(900),
            environment={
                "rds_cluster_identifier": rds_cluster_identifier,
                "docdb_cluster_identifier": docdb_cluster_identifier
            },
            code=lambda_.Code.from_asset(
                "assets/stop_all_services"
            ),
            handler="main.lambda_handler",
            initial_policy=[
                iam.PolicyStatement(
                    actions=[
                        "ecs:ListClusters",
                        "ecs:DescribeClusters",
                        "ecs:ListServices",
                        "ecs:DescribeServices",
                        "application-autoscaling:RegisterScalableTarget",
                        "rds:StopDBCluster",
                        "ec2:DescribeInstances",
                        "ec2:StopInstances",
                        "lambda:*",
                        "events:*"

                    ],
                    resources=["*"]
                )
            ])

        self.lambda_arn = self.lambda_function.function_arn

        # CloudWatch Event Rule that triggers Lambda Function
        if environment in ["test-hotfix-dev", "test-dev"]:
            self.event_rule = events.Rule(
                scope,
                id + "-" + "rule" + "-" + environment,
                enabled=metadata.get("stop_services")["enabled"],
                rule_name=id + "-" + "rule" + "-" + environment,
                schedule=events.Schedule.cron(
                    week_day=metadata.get(
                        "stop_services")["cron"]["week_day"],
                    hour=metadata.get("stop_services")["cron"]["hour"],
                    minute=metadata.get("stop_services")["cron"]["minute"],
                    month=metadata.get("stop_services")["cron"]["month"],
                    year=metadata.get("stop_services")["cron"]["year"]
                ),
            )

            self.cfn_event_rule = self.event_rule.node.children[0]
            self.cfn_event_rule.add_override(
                "Properties.Targets",
                [dict({
                    "Arn": self.lambda_arn,
                    "Id": self.lambda_function.function_name
                })]
            )

            # Lambda Invoke Permissions
            self.lambda_invoke = lambda_.CfnPermission(
                scope,
                id + "-" + "invoke-permission" + "-" + environment,
                action="lambda:InvokeFunction",
                function_name=self.lambda_function.function_name,
                principal="events.amazonaws.com",
                source_arn=self.event_rule.rule_arn
            )

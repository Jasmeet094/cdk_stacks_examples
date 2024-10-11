from aws_cdk import Duration
import aws_cdk.aws_events as events
import aws_cdk.aws_iam as iam
import aws_cdk.aws_lambda as lambda_


class LambdaEnvironmentUpdate:
    def __init__(
            self,
            scope,
            id,
            region,
            account_id,
            environment,
            event_enabled,
            secret_name,
            function_arn_list,
            assets_path,
            function_names,
            lambda_timeout,
            **kwargs):

        function_arn_list.append(
            f"arn:aws:kms:{region}:{account_id}:alias/aws/secretsmanager"
            )
        function_arn_list.append(
            f"arn:aws:secretsmanager:{region}:{account_id}:secret:{secret_name}" # noqa
            )

        self.lambda_function = lambda_.Function(
                scope,
                id + "-" + environment,
                function_name=id + "-" + environment,
                runtime=lambda_.Runtime.PYTHON_3_11,
                timeout=Duration.seconds(lambda_timeout),
                environment={
                    "FunctionNames": function_names,
                    "SecretArn": f"arn:aws:secretsmanager:{region}:{account_id}:secret:{secret_name}" # noqa
                },
                code=lambda_.Code.from_asset(
                    assets_path
                ),
                handler="main.lambda_handler",
                initial_policy=[
                    iam.PolicyStatement(
                        actions=[
                            "secretsmanager:GetSecretValue",
                            "kms:Decrypt",
                            "lambda:UpdateFunctionConfiguration"
                        ],
                        resources=function_arn_list
                    )
                ])
        self.lambda_arn = self.lambda_function.function_arn

        self.event_rule = events.Rule(
                scope,
                id + "-event-rule-" + environment,
                enabled=event_enabled,
                rule_name=id + "-event-rule-" + environment,
                event_pattern=events.EventPattern(
                    source=["aws.secretsmanager"],
                    detail={
                        "eventSource": ["secretsmanager.amazonaws.com"],
                        "eventName": ["UpdateSecret", "PutSecretValue"],
                        "requestParameters": {
                            "secretId": [
                                f"arn:aws:secretsmanager:{region}:{account_id}:secret:{secret_name}" # noqa
                                ]
                            }
                        }
                    )
            )
        self.cfn_event_rule = self.event_rule.node.children[0]
        self.cfn_event_rule.add_override(
            "Properties.Targets",
            [dict({
                "Arn": self.lambda_arn,
                "Id": self.lambda_function.function_name
            })]
        )

        self.lambda_invoke = lambda_.CfnPermission(
                scope,
                id + "-invoke-permission-" + environment,
                action="lambda:InvokeFunction",
                function_name=self.lambda_function.function_name,
                principal="events.amazonaws.com",
                source_arn=self.event_rule.rule_arn
            )

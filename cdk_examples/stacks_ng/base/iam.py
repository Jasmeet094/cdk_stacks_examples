from aws_cdk import (
    aws_iam as iam,
    CfnOutput
)


class ECSExecutionRole:

    def __init__(self, scope, id, environment, **kwargs):

        self.role = iam.Role(
            scope,
            id,
            assumed_by=iam.ServicePrincipal("ecs-tasks.amazonaws.com"),
            description="ECS execution role to pull image stored in ECR",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name('AmazonSSMReadOnlyAccess'),  # noqa
            ],
        )

        policy_name = 'ng-ecs-exec-base-policy'
        if environment in ["test-qa"]:
            policy_name = f"{environment}-ng-ecs-exec-base-policy"
        self.role.attach_inline_policy(
            iam.Policy(
                scope, policy_name,
                statements=[
                    iam.PolicyStatement(
                        effect=iam.Effect.ALLOW,
                        actions=[
                            "ssmmessages:CreateControlChannel",
                            "ssmmessages:CreateDataChannel",
                            "ssmmessages:OpenControlChannel",
                            "ssmmessages:OpenDataChannel",
                            "ecr:*",
                            "cloudwatch:*",
                            "logs:*",
                            "kinesis:*",
                            "sqs:*",
                            "secretsmanager:GetSecretValue",
                            "secretsmanager:DescribeSecret",
                            "s3:ListBucket",
                            "s3:PutObject",
                            "s3:GetObject",
                            "kms:Decrypt",
                            "kms:GenerateDataKey",
                        ],
                        resources=['*']
                            )
                ]
            )
        )

        CfnOutput(
            scope=scope,
            id="ng-ecs-task-exe-role-arn",
            value=self.role.role_arn,
            export_name="ng-ecs-task-exe-role-arn"
        )

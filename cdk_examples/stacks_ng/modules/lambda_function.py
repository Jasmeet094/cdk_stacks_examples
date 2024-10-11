from .environment import EnvVariables
from aws_cdk import (
  aws_ecr as ecr,
  aws_iam as iam,
  aws_lambda as _lambda,
  aws_ec2 as ec2,
  aws_secretsmanager as sm,
  Duration as Duration,
  aws_sqs as sqs,
  aws_cloudwatch as cloudwatch,
)


class DockerLambda:

    def get_environment_variables(
        self,
        scope,
        id,
        account_id,
        region,
        application_secrets
    ):
        if application_secrets != "":
            env_vars = getattr(EnvVariables, application_secrets)
            secret_env_vars = {}
            for item in env_vars:
                secret_env_vars[item] = sm.Secret.from_secret_attributes(
                    scope,
                    id + "-" + item,
                    secret_partial_arn=f"arn:aws:secretsmanager:{region}:{account_id}:secret:{application_secrets}" # noqa
                ).secret_value_from_json(item).to_string()
            return secret_env_vars
        else:
            return {}

    def enable_dead_letter_queue(
            self,
            scope,
            id,
            enable_dlq,
            sns_arn,
            environment):

        if not enable_dlq:
            return None
        else:
            # Create SQS for AWS Lambda DLQ
            sqs_queue = sqs.Queue(
                    scope,
                    id + "sqs" + environment,
                    visibility_timeout=Duration.seconds(1800),
                )

            # Alarm
            cloudwatch.CfnAlarm(
                scope,
                id + "sqs-alarm" + environment,
                alarm_name=id + "sqs-alarm" + environment,
                comparison_operator='GreaterThanThreshold',
                evaluation_periods=1,
                threshold=0,
                metric_name='ApproximateNumberOfMessagesVisible',
                namespace='AWS/SQS',
                period=60,
                dimensions=[
                    cloudwatch.CfnAlarm.DimensionProperty(
                        name='QueueName',
                        value=sqs_queue.queue_name
                    )
                ],
                statistic='Average',
                alarm_description=id + " " + 'Lambda Dead Letter Queue Alarm',
                alarm_actions=[sns_arn]
            )

            dead_letter_queue = sqs_queue.from_queue_arn(
                scope,
                id + "sqs-arn" + environment,
                queue_arn=sqs_queue.queue_arn
            )

            return dead_letter_queue

    def __init__(
            self,
            scope,
            id,
            environment,
            ecr_name,
            vpc_id,
            account_id,
            region,
            cmd=[],
            timeout=600,
            memory_size=1024,
            enable_dlq=False,
            sns_arn="",
            environment_variables={},
            application_secrets="",
            **kwargs):

        common_environment_variables = {
            "DD_SERVICE": environment + "-" + id,
            "DeploymentEnvironment": environment.split("-")[1]
        }

        self.function = _lambda.DockerImageFunction(
            scope,
            id + "-" + environment,
            function_name=environment + "-" + id if environment != "test-prod-secondary" else "2ry-" + id, # noqa
            description="NextGen Lambda function created by Stacks-NG",
            environment={**environment_variables, **self.get_environment_variables(scope, id, account_id, region, application_secrets), **common_environment_variables}, # noqa
            timeout=Duration.seconds(timeout),
            memory_size=memory_size,

            vpc=ec2.Vpc.from_lookup(scope, id, vpc_id=vpc_id),
            vpc_subnets=ec2.SubnetSelection(
                subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS
            ),

            code=_lambda.DockerImageCode.from_ecr(
                repository=ecr.Repository.from_repository_name(
                    scope,
                    id+ecr_name,
                    ecr_name),
                cmd=cmd,
            ),
            dead_letter_queue_enabled=enable_dlq,
            dead_letter_queue=self.enable_dead_letter_queue(
                scope,
                id,
                enable_dlq,
                sns_arn,
                environment
            )
        )

        self.function.add_to_role_policy(
            iam.PolicyStatement(
                actions=[
                    "s3:*",
                    "sqs:*",
                    "lambda:*",
                    "kms:GenerateDataKey",
                    "kms:Decrypt",
                    "secretsmanager:GetResourcePolicy",
                    "secretsmanager:GetSecretValue",
                    "secretsmanager:DescribeSecret",
                    "secretsmanager:ListSecretVersionIds"
                ],
                resources=["*"],
            )
        )

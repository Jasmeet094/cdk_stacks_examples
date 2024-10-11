from aws_cdk import aws_iam as iam
from aws_cdk.aws_s3 import CfnBucketPolicy
from aws_cdk import Stack, Fn


class Stack(Stack):

    def __init__(self,
                 scope,
                 id,
                 environment,
                 metadata:
                 dict,
                 **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        # Static content bucket policy
        bucket_name = f"test-platform-static-files-bucket-{environment}"

        bucket_arn = "arn:aws:s3:::"+bucket_name

        oai_id = Fn.import_value(
            "oai-id-"+environment+"-"+"test-platform-cloudfront"
        )

        ecs_exe_role_arn = Fn.import_value(
            'ng-ecs-task-exe-role-arn'
        )
        ecs_exe_role = iam.Role.from_role_arn(self,
                                              id="ng-ecs-task-exe-role",
                                              role_arn=ecs_exe_role_arn)
        policy_document = iam.PolicyDocument(
            statements=[
                iam.PolicyStatement(
                    actions=['s3:GetObject'],
                    principals=[
                        iam.ArnPrincipal(
                            "arn:aws:iam::cloudfront:" +
                            "user/CloudFront Origin Access Identity"
                            + " " +
                            str(oai_id))
                    ],
                    resources=[f'{bucket_arn}/*']
                ),
                iam.PolicyStatement(
                    actions=["s3:*"],
                    principals=[
                        ecs_exe_role
                    ],
                    resources=[f'{bucket_arn}/*']
                )
            ]
        )

        CfnBucketPolicy(
            self,
            id,
            bucket=bucket_name,
            policy_document=policy_document
        )

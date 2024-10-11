from constructs import Construct
from aws_cdk import (
  Stack as stack,
  aws_kms as kms,
  Fn,
)


class Stack(stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        super_user_role = f"arn:aws:iam::{metadata.get('id')}:role/superuser_role" # noqa
        ecs_execution_role_arn = Fn.import_value('ng-ecs-task-exe-role-arn')

        kms_key = kms.CfnKey(
                self,
                construct_id+"-JPM_CBM-"+environment,
                description="Key JPM_CBM use to encrypt and decrypt",
                multi_region=True,
                pending_window_in_days=7,
                key_policy={
                    "Version": "2012-10-17",
                    "Id": "key-default-1",
                    "Statement": [
                        {
                            "Sid": "Enable IAM User Permissions",
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": f"arn:aws:iam::{metadata.get('id')}:root" # noqa
                            },
                            "Action": "kms:*",
                            "Resource": "*"
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": f"{super_user_role}"
                            },
                            "Action": "kms:*",
                            "Resource": "*"
                        },
                        {
                            "Effect": "Allow",
                            "Principal": {
                                "AWS": f"{ecs_execution_role_arn}"
                            },
                            "Action": [
                                "kms:Decrypt",
                                "kms:Encrypt",
                                "kms:GenerateDataKey*",
                                "kms:ReEncrypt*"
                            ],
                            "Resource": "*"
                        }
                    ]
                }
            )

        kms.CfnAlias(
            self,
            construct_id+"-JPM_CBM-alias-"+environment,
            alias_name="alias/JPM_CBM",
            target_key_id=kms_key.attr_key_id
        )

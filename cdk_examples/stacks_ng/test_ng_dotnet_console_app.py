from aws_cdk import (
    aws_iam as iam,
    aws_ec2 as ec2,
    aws_secretsmanager as secretsmanager,
    Tags
)
import aws_cdk as cdk
from constructs import Construct
from aws_cdk import Stack


class DotNetConsoleApp(Stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            public_ipv4_pool=None,
            tags=None,
            **kwargs) -> None:
        super().__init__(
            scope, construct_id, **kwargs)

        self.vpcid = "ng-vpc-id"+"-"+environment
        self.dotnetsg = "ng-dotnet-console-app-security-group"+"-"+environment
        self.subnets = "ng-private-subnets"+"-"+environment
        self.split_subnets = cdk.Fn.select(
            0,  # always pick subnet on 0 index
            cdk.Fn.split(
                ",",
                cdk.Fn.import_value(
                    self.subnets
                )
            )
        )

        # arn of secret manager secret certificate
        certificate_secret_arn = secretsmanager.Secret.from_secret_name_v2(
            self,
            id=construct_id+"-certificate-"+environment,
            secret_name="Certificates"
        )

        # arn of secret manager secret test_ng_console_app
        console_app_secret_arn = secretsmanager.Secret.from_secret_name_v2(
            self,
            id=construct_id+"-test_ng_console_app-"+environment,
            secret_name="test_ng_console_app"
        )

        # arn of secret datadog_api
        datadog_api_arn = secretsmanager.Secret.from_secret_name_v2(
            self,
            id=construct_id+"-datadog_api-"+environment,
            secret_name="datadog_api_key"
        )

        # arn of secret manager dotnet console users
        dotnet_console_users = secretsmanager.Secret.from_secret_name_v2(
            self,
            id=construct_id+"-dotnet_users-"+environment,
            secret_name="dotnet-console-app-users"
        )

        # ARN of KMS KEY
        kms_key_id = self.node.try_get_context(environment)['kmsKeyId']
        kms_arn = f"arn:aws:kms:{self.region}:{self.account}:key/{kms_key_id}"

        dotnet_role = iam.Role(
            self,
            construct_id+'-role-'+environment,
            assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
            role_name=construct_id+'-role-'+environment
        )

        dotnet_role.add_to_policy(iam.PolicyStatement(
            resources=[
                f"{certificate_secret_arn.secret_arn}-*",
                f"{console_app_secret_arn.secret_arn}-*",
                f"{datadog_api_arn.secret_arn}-*",
                f"{dotnet_console_users.secret_arn}-*",
                kms_arn
            ],
            actions=[
                "secretsmanager:GetSecretValue",
                "secretsmanager:DescribeSecret",
                "kms:Decrypt",
                "kms:GenerateDataKey"
                ]
        ))

        dotnet_role.add_to_policy(iam.PolicyStatement(
            resources=["*"],
            actions=[
                "s3:ListStorageLensConfigurations",
                "s3:ListAccessPointsForObjectLambda",
                "s3:GetAccessPoint",
                "s3:PutAccountPublicAccessBlock",
                "s3:GetAccountPublicAccessBlock",
                "s3:ListAllMyBuckets",
                "s3:ListAccessPoints",
                "s3:PutAccessPointPublicAccessBlock",
                "s3:ListJobs",
                "s3:PutStorageLensConfiguration",
                "s3:ListMultiRegionAccessPoints",
                "s3:CreateJob",
                "s3:ListBucket",
                "s3:GetObject",
                ]
        ))

        s3_arn_list = metadata.get("dotnet_ec2", {}).get("s3_arn", [])
        if s3_arn_list:
            dotnet_role.add_to_policy(iam.PolicyStatement(
                resources=[
                    f"arn:aws:s3:::{arn}/*" for arn in s3_arn_list
                ],
                actions=["s3:*"]
            ))

        dotnet_role.add_managed_policy(
            iam.ManagedPolicy.from_aws_managed_policy_name(
                'AmazonSSMManagedInstanceCore'
            )
        )

        iam.CfnInstanceProfile(
            self,
            id=construct_id+"-profile-"+environment,
            roles=[dotnet_role.role_name],
            instance_profile_name=construct_id+"-profile-"+environment,
        )

        with open('./stacks_ng/templates/dotnet_user_data.sh', 'r') as f:
            user_data = f.read()

        # Image ID based on the Env Prod and Dev
        if environment in ["test-prod", "test-dev"]:
            image_id = metadata.get("dotnet_ec2")["cis_image_id"]

        else:
            image_id = metadata.get("dotnet_ec2")["image_id"]

        dotnet_instance = ec2.CfnInstance(
            self,
            construct_id,
            image_id=image_id,
            instance_type=metadata.get("dotnet_ec2")["instance_type"],
            key_name=metadata.get("dotnet_ec2")["pem_key"],
            security_group_ids=[cdk.Fn.import_value(self.dotnetsg)],
            subnet_id=self.split_subnets,
            iam_instance_profile=construct_id+"-profile-"+environment,
            private_ip_address=metadata.get("dotnet_ec2")["private_ip"],
            block_device_mappings=[ec2.CfnInstance.BlockDeviceMappingProperty(
                device_name="/dev/sda1",
                ebs=ec2.CfnInstance.EbsProperty(
                    volume_size=30,
                    delete_on_termination=True,
                    volume_type="gp2",
                    encrypted=False
                )
            )],
            user_data=cdk.Fn.base64(user_data)
        )

        # adding tags to instance
        Tags.of(dotnet_instance).add("Name", "fx-ng-dotnet-console-app")
        Tags.of(dotnet_instance).add("ENV", environment)
        Tags.of(dotnet_instance).add("Owner", "test")

        split_env = environment.split("-", 1)
        environment = split_env[1]

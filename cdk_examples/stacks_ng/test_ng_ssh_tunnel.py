from aws_cdk import (
    aws_route53 as route53,
    aws_iam as iam,
    aws_ec2 as ec2,
    Tags
)
import aws_cdk as cdk
from random import randint
from constructs import Construct
from aws_cdk import Stack


class testSSHTunnel(Stack):

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

        zone_id = metadata.get('hostedZoneId')
        zone_name = metadata.get('hostedZone')

        route53.HostedZone.from_hosted_zone_attributes(
            self,
            'id'+zone_name,
            hosted_zone_id=zone_id,
            zone_name=zone_name
        )

        subnet_selection = randint(0, 2)

        self.vpcid = "ng-vpc-id"+"-"+environment
        self.sshsg = "ng-ssh-tunnel-securitygroup"+"-"+environment
        self.subnets = "ng-public-subnets"+"-"+environment
        self.split_subnets = cdk.Fn.select(
            subnet_selection,
            cdk.Fn.split(
                ",",
                cdk.Fn.import_value(
                    self.subnets
                )
            )
        )

        if environment not in ["test-prod-secondary", "test-qa"]:
            ssh_tunnel_role = iam.Role(
                self,
                "ng_ssh_tunnel_role"+"-"+construct_id,
                assumed_by=iam.ServicePrincipal("ec2.amazonaws.com"),
                role_name='ng_ssh_tunnel_role'
            )

            ssh_tunnel_role.add_to_policy(iam.PolicyStatement(
                resources=["*"],
                actions=[
                    "s3:GetObject",
                    "secretsmanager:GetSecretValue"
                    ]
            ))

            ssh_tunnel_role.add_managed_policy(
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'AmazonSSMManagedInstanceCore'
                )
            )

            iam.CfnInstanceProfile(
                self,
                id="ng_ssh_tunnel_profile"+"-"+construct_id,
                roles=[ssh_tunnel_role.role_name],
                instance_profile_name="ng_ssh_tunnel_instance_profile",
            )

        with open('./stacks_ng/templates/ssh_user_data.sh', 'r') as f:
            user_data = f.read()

        # CIS AMI ID to use for prod and dev env
        if environment in ["test-prod", "test-dev"]:
            ami_id = metadata.get("ec2")["ami_id"]
        else:
            ami_id = ec2.AmazonLinuxImage(
                generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2
            ).get_image(self).image_id

        ssh_tunnel_instance = ec2.CfnInstance(
            self,
            construct_id,
            image_id=ami_id,
            instance_type=metadata.get("ec2")["instance_type"],
            key_name=metadata.get("ec2")["pem_key"],
            security_group_ids=[cdk.Fn.import_value(self.sshsg)],
            subnet_id=self.split_subnets,
            iam_instance_profile="ng_ssh_tunnel_instance_profile",
            user_data=cdk.Fn.base64(user_data)
        )

        # adding tags to instance
        Tags.of(ssh_tunnel_instance).add("Name", "ng_ssh_tunnel_instance")
        Tags.of(ssh_tunnel_instance).add("ENV", environment)
        Tags.of(ssh_tunnel_instance).add("Owner", "test")

        ssh_eip = ec2.CfnEIP(
                    self,
                    id="SSHTunnel-EIP-"+construct_id+"-"+environment,
                    instance_id=ssh_tunnel_instance.ref,
                    domain='vpc',
                    public_ipv4_pool=public_ipv4_pool
                )

        # adding tags to elastic ip
        Tags.of(ssh_eip).add("Name", "SSHTunnelElasticIP")
        Tags.of(ssh_eip).add("ENV", environment)
        Tags.of(ssh_eip).add("Owner", "test")

        split_env = environment.split("-", 1)
        environment = split_env[1]
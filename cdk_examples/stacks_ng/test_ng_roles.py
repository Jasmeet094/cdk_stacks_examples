from aws_cdk import (
    Stack as stack,
    aws_iam as iam
)
from constructs import Construct


class Stack(stack):

    def __init__(
            self,
            scope: Construct,
            id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, id, **kwargs)

        if environment != "test-master":
            # IAM Cross Account Role for VPC Peering
            cross_account_ids = metadata.get("cross_account_peering")[
                "cross_account_ids"]
            if cross_account_ids:
                peering_cross_account_role = iam.Role(
                    self, "Role",
                    assumed_by=iam.CompositePrincipal(
                        *[iam.AccountPrincipal(account_id) for account_id in cross_account_ids]  # noqa
                    ),
                    role_name=id+"-cross-account"+"-"+environment,
                )

                # Define the VPC peering permissions
                peering_cross_account_policy = iam.PolicyStatement(
                    actions=[
                        "ec2:CreateVpcPeeringConnection",
                        "ec2:AcceptVpcPeeringConnection"
                    ],
                    resources=["*"]
                )

                peering_cross_account_role.add_to_policy(
                    peering_cross_account_policy)

        # AWS Cross Account Billing role

        master_account = self.node.try_get_context("test-master")['id']
        master_principal = iam.AccountPrincipal(master_account)
        master_principal = master_principal.with_conditions(
            {'Bool': {'aws:MultiFactorAuthPresent': True}}
        )

        iam.Role(
            self,
            id+"-billing"+"-"+environment,
            assumed_by=master_principal,
            role_name="billing_role",
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "job-function/Billing"),
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    "AWSBillingConductorFullAccess")
            ],
        )

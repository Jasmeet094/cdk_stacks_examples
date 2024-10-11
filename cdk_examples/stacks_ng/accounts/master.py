from aws_cdk import (
    aws_iam as iam
)
from aws_cdk import Stack as stack


class Stack(stack):

    def __init__(self, scope, id, metadata: dict, **kwargs):
        super().__init__(scope, id, **kwargs)
        subaccounts = [
            self.node.try_get_context('finexio-master')['id'],
            self.node.try_get_context('finexio-dev')['id'],
            self.node.try_get_context('finexio-stage')['id'],
            self.node.try_get_context('finexio-sandbox')['id'],
            self.node.try_get_context('finexio-demo')['id'],
            self.node.try_get_context('finexio-hotfix-dev')['id'],
            self.node.try_get_context('finexio-qa-new')['id'],
            self.node.try_get_context('finexio-prod')['id'],
        ]

        billing_existing_users = []
        billing_user_names = metadata.get("iam_users_group")[
            "billing_group"]

        for user in billing_user_names:
            billing_existing_users.append(
                iam.User.from_user_name(
                    self,
                    "billing_group_"+user,
                    user_name=user
                )
            )

        # Groups
        billing_group = iam.Group(
            self,
            'billing_group',
            group_name='billing_group')

        # Policies
        # policies that allow master account users to assume subaccount roles
        group_assumable_roles = {
            'billing_role': [billing_group],
        }
        for role, groups in group_assumable_roles.items():
            role_arns = [
                f'arn:aws:iam::{account_id}:role/{role}'
                for account_id in subaccounts
            ]
            iam.Policy(
                self,
                f'assume_subaccount_{role}_policy',
                groups=groups,
                statements=[
                    iam.PolicyStatement(
                        actions=['sts:AssumeRole'],
                        resources=role_arns,
                    )
                ]
            )

        # Attach existing IAM users to the group called billing
        for user in billing_existing_users:
            billing_group.add_user(user)

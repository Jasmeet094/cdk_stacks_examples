from aws_cdk import (
    Stack as stack
)
from aws_cdk import aws_ec2
from constructs import Construct


class Stack(stack):

    def peering_connection(
            self,
            id,
            acceptor,
            requestor,
            region,
            vpc_id_requester,
            vpc_id_acceptor,
            account_id_acceptor,
            vpc_cidr_acceptor,
            route_table_ids,
            environment,
            ):

        # cross account role for vpc peering
        peering_cross_account_arn = "arn:aws:iam::" \
            + account_id_acceptor + \
            ":role/test-ng-role-cross-account-test-" \
            + acceptor

        # peering connection
        peering_connection = aws_ec2.CfnVPCPeeringConnection(
            self,
            id+"-"+environment,
            vpc_id=vpc_id_requester,
            peer_vpc_id=vpc_id_acceptor,
            peer_owner_id=account_id_acceptor,
            peer_region=region,
            peer_role_arn=peering_cross_account_arn
        )

        # adding routes in the Requestor VPC
        for route_table_id in route_table_ids:
            aws_ec2.CfnRoute(
                self,
                id+"-"+route_table_id+"-"+environment,
                route_table_id=route_table_id,
                destination_cidr_block=vpc_cidr_acceptor,
                vpc_peering_connection_id=peering_connection.attr_id
            )

    def __init__(
            self,
            scope: Construct,
            id: str,
            requestor: str,
            acceptor: str,
            metadata: dict,
            legacy_peering=False,  # peering connection with legacy stack
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, id, **kwargs)

        region = metadata.get('region')
        vpc_id_requester = metadata.get('vpc_id')
        account_id_acceptor = self.node.try_get_context(
            "test-"+acceptor)["id"]
        route_table_ids = metadata.get("route_table_ids")

        # Peering between ng and legacy stacks
        if legacy_peering:
            vpc_id_acceptor = self.node.try_get_context(
                "test-"+acceptor)["v1_stacks"]["vpc_id"]
            vpc_cidr_acceptor = self.node.try_get_context(
                "test-"+acceptor)["v1_stacks"]["cidr"]

            self.peering_connection(
                id,
                acceptor,
                requestor,
                region,
                vpc_id_requester,
                vpc_id_acceptor,
                account_id_acceptor,
                vpc_cidr_acceptor,
                route_table_ids,
                environment
            )
        else:  # Peering between ng stacks
            vpc_id_acceptor = self.node.try_get_context(
                "test-"+acceptor)["vpc_id"]
            vpc_cidr_acceptor = self.node.try_get_context(
                "test-"+acceptor)["cidr"]
            self.peering_connection(
                id,
                acceptor,
                requestor,
                region,
                vpc_id_requester,
                vpc_id_acceptor,
                account_id_acceptor,
                vpc_cidr_acceptor,
                route_table_ids,
                environment
            )

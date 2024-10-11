from aws_cdk import (
    Stack as stack,
)
from aws_cdk import aws_ec2
from constructs import Construct


class Stack(stack):

    def peering_connection(
            self,
            id,
            requestor,
            vpc_cidr_requestor,
            route_table_ids,
            peering_connection_id,
            environment
            ):

        # adding routes in the Acceptor VPC
        for route_table_id in route_table_ids:
            aws_ec2.CfnRoute(
                self,
                id+"-"+route_table_id+"-"+environment,
                route_table_id=route_table_id,
                destination_cidr_block=vpc_cidr_requestor,
                vpc_peering_connection_id=peering_connection_id
            )

    def __init__(
            self,
            scope: Construct,
            id: str,
            requestor: str,
            acceptor: str,
            metadata: dict,
            legacy_peering=False,
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, id, **kwargs)

        vpc_cidr_requestor = self.node.try_get_context("test-"+requestor)[
            "cidr"]

        if legacy_peering:
            route_table_ids = metadata.get("v1_stacks")["legacy_route_table_ids"]  # noqa
            peering_connection_id = metadata.get("peering_connection_ids")[
                requestor+"_"+"legacy_"+acceptor+"_"+"peering_id"]
            self.peering_connection(
                id,
                requestor,
                vpc_cidr_requestor,
                route_table_ids,
                peering_connection_id,
                environment
            )
        else:
            route_table_ids = metadata.get("route_table_ids")
            peering_connection_id = metadata.get("peering_connection_ids")[
                requestor+"_"+acceptor+"_"+"peering_id"]
            self.peering_connection(
                id,
                requestor,
                vpc_cidr_requestor,
                route_table_ids,
                peering_connection_id,
                environment
            )

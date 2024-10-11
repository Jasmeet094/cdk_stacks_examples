from aws_cdk import (
    aws_ec2 as ec2,
    CfnOutput,
    Tags
)


class Network:

    DEFAULT_MAX_AZS = 3
    DEFAULT_NAT_GATEWAYS = 1
    DEFAULT_SUBNET_CIDR_MASK = 24

    def __init__(self, scope, id, environment, cidr, metadata, **kwargs):

        self.scope = scope
        self.id = id
        self.environment = environment
        self.cidr = cidr
        self.metadata = metadata
        self.kwargs = kwargs

        # VPC
        self.vpc = self.create_vpc()

        # VPC flow log
        self.flowlog = self.create_flow_log()

        # Subnets
        self.private_subnet_ids, self.public_subnet_ids = self.get_subnet_ids()

        # VPC endpoints
        self.add_endpoints()

        # Security groups
        self.create_security_groups()

        # VPC Peering
        self.setup_vpc_peering()

        # Output of stack
        self.add_cfn_outputs()

        # Tag all VPC Resources
        self.add_tags()

    def create_vpc(self):
        return ec2.Vpc(
            self.scope,
            f"vpc-{self.id}-{self.environment}",
            ip_addresses=ec2.IpAddresses.cidr(
                cidr_block=self.cidr
            ),
            max_azs=self.kwargs.get("max_azs", self.DEFAULT_MAX_AZS),
            nat_gateways=self.kwargs.get("nat_gateways", self.DEFAULT_NAT_GATEWAYS),  # noqa
            subnet_configuration=self.get_subnet_configuration()
        )

    def get_subnet_configuration(self):
        subnet_mask = self.kwargs.get("subnet_cidr_mask", self.DEFAULT_SUBNET_CIDR_MASK)  # noqa
        return [
            ec2.SubnetConfiguration(name="public-", cidr_mask=subnet_mask, subnet_type=ec2.SubnetType.PUBLIC),  # noqa
            ec2.SubnetConfiguration(name="private-", cidr_mask=subnet_mask, subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)  # noqa
        ]

    def create_flow_log(self):
        return ec2.FlowLog(
            self.scope,
            "vpc-flowlog",
            resource_type=ec2.FlowLogResourceType.from_vpc(self.vpc),
            traffic_type=ec2.FlowLogTrafficType.REJECT
        )

    def get_subnet_ids(self):
        private_subnet_ids = self.vpc.select_subnets(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS).subnet_ids  # noqa
        public_subnet_ids = self.vpc.select_subnets(subnet_type=ec2.SubnetType.PUBLIC).subnet_ids  # noqa
        return private_subnet_ids, public_subnet_ids

    def add_endpoints(self):
        self.s3_endpoint = self.vpc.add_gateway_endpoint('S3', service=ec2.GatewayVpcEndpointAwsService.S3)  # noqa
        self.ecs_endpoint = self.vpc.add_interface_endpoint('ECS', service=ec2.InterfaceVpcEndpointAwsService.ECS)  # noqa
        self.cw_endpoint = self.vpc.add_interface_endpoint('CLOUDWATCH',
                                                           service=ec2.InterfaceVpcEndpointAwsService.CLOUDWATCH)  # noqa
        self.sqs_endpoint = self.vpc.add_interface_endpoint('SQS', service=ec2.InterfaceVpcEndpointAwsService.SQS)  # noqa

    def create_security_groups(self):
        self.securityGroup = ec2.SecurityGroup(
            self.scope, id="default", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        self.elasticacheSecurityGroupProperties = ec2.SecurityGroup(
            self.scope, id=self.id + "-REDISSG", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        self.elasticacheSecurityGroup = self \
            .elasticacheSecurityGroupProperties.security_group_id

        self.ALBSecurityGroup = ec2.SecurityGroup(
            self.scope, id=self.id + "-ALB", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        self.ALBSecurityGroup.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            connection=ec2.Port.tcp(80)
        )

        self.ALBSecurityGroup.add_ingress_rule(
            peer=ec2.Peer.ipv4("0.0.0.0/0"),
            connection=ec2.Port.tcp(443)
        )

        # SG for App ECS Services
        self.ServiceSecurityGroup = ec2.SecurityGroup(
            self.scope, id=self.id + "SVC", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        self.ServiceSecurityGroup.add_ingress_rule(
            peer=ec2.Peer.ipv4(self.cidr),
            connection=ec2.Port.tcp(443)
        )

        self.ServiceSecurityGroup.add_ingress_rule(
            peer=self.ALBSecurityGroup,
            connection=ec2.Port.tcp(443)
        )

        self.DocumentdbSecurityGroup = ec2.SecurityGroup(
            self.scope, id=self.id + "DOCUMENTDB", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        for pvt_subnet in self.metadata.get("private_subnet_cidrs"):
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(pvt_subnet),
                connection=ec2.Port.tcp(27017)
            )
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(pvt_subnet),
                connection=ec2.Port.tcp(27018)
            )
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(pvt_subnet),
                connection=ec2.Port.tcp(27019)
            )
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(pvt_subnet),
                connection=ec2.Port.tcp(27020)
            )

        # vpc cidr for cross account peering connection
        for vpc_cidr in self.metadata.get("cross_account_peering")[
                "cross_account_vpc_cidr"]:
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(vpc_cidr),
                connection=ec2.Port.tcp(27017)
            )
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(vpc_cidr),
                connection=ec2.Port.tcp(27018)
            )
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(vpc_cidr),
                connection=ec2.Port.tcp(27019)
            )
            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(vpc_cidr),
                connection=ec2.Port.tcp(27020)
            )

        self.elasticacheSecurityGroupProperties.add_ingress_rule(
            peer=self.ServiceSecurityGroup,
            connection=ec2.Port.tcp(6379)
        )

        # vpc cidr for cross account peering connection
        for vpc_cidr in self.metadata.get("cross_account_peering")[
                "cross_account_vpc_cidr"]:
            self.elasticacheSecurityGroupProperties.add_ingress_rule(
                peer=ec2.Peer.ipv4(vpc_cidr),
                connection=ec2.Port.tcp(6379)
            )

        # SG for ECS private api service ng-services-api
        self.PrivateServiceSecurityGroup = ec2.SecurityGroup(
            self.scope, id=self.id + "-ecs-private-api",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        for public_subnet in self.metadata.get("public_subnet_cidrs"):
            self.PrivateServiceSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(public_subnet),
                connection=ec2.Port.tcp(443)
            )

        # SG for ECS api service
        self.ApiServiceSecurityGroup = ec2.SecurityGroup(
            self.scope, id=self.id + "-ecs-api", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        self.ApiServiceSecurityGroup.add_ingress_rule(
            peer=self.ServiceSecurityGroup,
            connection=ec2.Port.tcp(443)
        )

        # SG for Dot Net Console Application
        self.DotNetConsoleAppSecurityGroup = ec2.SecurityGroup(
            self.scope, id=self.id + "-DotNetConsoleApp", vpc=self.vpc, allow_all_outbound=True  # noqa
        )

        for ip in self.metadata.get("dotnet_ec2")["sg_inbound_ip"]:
            self.DotNetConsoleAppSecurityGroup.add_ingress_rule(
                peer=ec2.Peer.ipv4(ip),
                connection=ec2.Port.tcp(22)
            )

        # Allow Dotnet EC2 to access to the Documentdb
        self.DocumentdbSecurityGroup.add_ingress_rule(
            peer=self.DotNetConsoleAppSecurityGroup,
            connection=ec2.Port.tcp_range(27017, 27020)
        )

    def add_cfn_outputs(self):
        CfnOutput(
            scope=self.scope,
            id="vpc_id",
            value=self.vpc.vpc_id,
            export_name="ng-vpc-id" + "-" + self.environment
        )

        CfnOutput(
            scope=self.scope,
            id="public_subnets",
            value=','.join([x.subnet_id for x in self.vpc.public_subnets]),
            export_name="ng-public-subnets" + "-" + self.environment
        )

        CfnOutput(
            scope=self.scope,
            id="private_subnets",
            value=','.join([x.subnet_id for x in self.vpc.private_subnets]),
            export_name="ng-private-subnets" + "-" + self.environment
        )

        CfnOutput(
            scope=self.scope,
            id="ecs_services_security_group",
            value=str(self.ServiceSecurityGroup.security_group_id),
            export_name="ng-ecs-services-security-group" + "-" + self.environment  # noqa
        )

        # Export SG id for ECS private services
        CfnOutput(
            scope=self.scope,
            id="ecs_private_api_services_security_group",
            value=str(self.PrivateServiceSecurityGroup.security_group_id),
            export_name="ng-ecs-private-api-services-security-group" + "-" + self.environment  # noqa
        )

        # Export SG id for ECS api services
        CfnOutput(
            scope=self.scope,
            id="ecs_api_services_security_group",
            value=str(self.ApiServiceSecurityGroup.security_group_id),
            export_name="ng-ecs-api-services-security-group" + "-" + self.environment  # noqa
        )

        # Export SG id of Dot Net Console Application
        CfnOutput(
            scope=self.scope,
            id="dotnet_console_app_security_group",
            value=str(self.DotNetConsoleAppSecurityGroup.security_group_id),
            export_name="ng-dotnet-console-app-security-group" + "-" + self.environment  # noqa
        )

    def setup_vpc_peering(self):

        if self.environment not in ["test-sandbox",
                                    "test-demo",
                                    "test-hotfix-dev"]:
            self.peering = ec2.CfnVPCPeeringConnection(
                self.scope,
                "peering-" + self.id + "-" + self.environment,
                peer_vpc_id=self.metadata.get("v1_stacks")["vpc_id"],
                vpc_id=self.vpc.vpc_id,
                peer_owner_id=self.metadata.get("id"),
                peer_region=self.metadata.get("region")
            )
            n = 1
            for subnet in self.vpc.public_subnets + self.vpc.private_subnets:
                ec2.CfnRoute(
                    self.scope,
                    "peer-route-" + str(n),
                    route_table_id=subnet.route_table.route_table_id,
                    destination_cidr_block=self.metadata.get("v1_stacks")["cidr"],  # noqa
                    vpc_peering_connection_id=self.peering.ref
                )
                n += 1

            self.SSHTunnelSecurityGroup = self.ssh_tunnel_security_group(
                scope=self.scope,
                id=self.id,
                metadata=self.metadata
            )

            self.DocumentdbSecurityGroup.add_ingress_rule(
                peer=self.SSHTunnelSecurityGroup,
                connection=ec2.Port.tcp_range(27017, 27020)
            )

            # DotNet SG to allow traffic from ng ssh instance
            self.DotNetConsoleAppSecurityGroup.add_ingress_rule(
                peer=self.SSHTunnelSecurityGroup,
                connection=ec2.Port.tcp(22)
            )

            CfnOutput(
                scope=self.scope,
                id="ssh_tunnel_security_group",
                value=str(self.SSHTunnelSecurityGroup.security_group_id),
                export_name="ng-ssh-tunnel-securitygroup" + "-" + self.environment  # noqa
            )

            CfnOutput(
                scope=self.scope,
                id="Peering_id",
                value=self.peering.attr_id,
                export_name="ng-vpc-peering-id" + "-" + self.environment
            )

    def add_tags(self):
        Tags.of(self.scope).add(
            key="Owner", value=self.id, include_resource_types=[]
        )
        Tags.of(self.scope).add(
            key="ENV", value=self.environment, include_resource_types=[]
        )

    def ssh_tunnel_security_group(self, scope, id, metadata):
        """
            Security group for SSH Tunnel Instance
        """
        ssh_tunnel_security_group = ec2.SecurityGroup(
            scope,
            id=id + "-SSH-Tunnel",
            vpc=self.vpc,
            allow_all_outbound=True
        )

        # FiveTrans IPs - https://fivetran.com/docs/getting-started/ips
        ssh_tunnel_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("35.227.135.0/29"),
            connection=ec2.Port.tcp(22),
            description="FiveTrans"
        )

        ssh_tunnel_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("35.234.176.144/29"),
            connection=ec2.Port.tcp(22),
            description="FiveTrans"
        )

        ssh_tunnel_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("52.0.2.4/32"),
            connection=ec2.Port.tcp(22),
            description="FiveTrans"
        )

        # NordVPN test Gateway
        ssh_tunnel_security_group.add_ingress_rule(
            peer=ec2.Peer.ipv4("193.239.87.85/32"),
            connection=ec2.Port.tcp(22),
            description="NordVPN"
        )

        return ssh_tunnel_security_group

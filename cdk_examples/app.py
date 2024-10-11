#!/usr/bin/env python3

from aws_cdk import (
    App,
    Tags,
    Environment,
    aws_ec2 as ec2
)
from stacks_ng.accounts import master
from stacks_ng.test_ng import Stack as testStack
from stacks_ng.test_lambdas_ingestion import Stack as testLambdasIngestion  # noqa
from stacks_ng.test_ng_portal import Stack as testNGPortal
from stacks_ng.test_ng_admin import Stack as testNGAdminStack
from stacks_ng.test_ng_services_api import Stack as testNGServicesApiStack  # noqa
from stacks_ng.test_ng_mock import Stack as testNGMockStack # noqa
from stacks_ng.test_ng_docusign import Stack as testNGDocusign # noqa
from stacks_ng.test_ng_docusign_api import Stack as testNGDocusignApi # noqa
from stacks_ng.test_ng_ssh_tunnel import testSSHTunnel
from stacks_ng.test_lambdas_funding import Stack as testLambdasFunding  # noqa
from stacks_ng.test_lambdas_enrichment import Stack as testLambdasEnrichment  # noqa
from stacks_ng.test_lambdas_cardreloads import Stack as testLambdasCardReloads  # noqa
from stacks_ng.test_lambdas_disbursement import Stack as testLambdasDisbursement  # noqa
from stacks_ng.test_lambdas_notification import Stack as testLambdasNotification  # noqa
from stacks_ng.test_lambdas_compliance import Stack as testLambdasCompliance  # noqa
from stacks_ng.test_lambdas_sequencing import Stack as testLambdasSequencing  # noqa
from stacks_ng.test_lambdas_correction import Stack as testLambdasCorrection  # noqa
from stacks_ng.test_lambdas_env_update import Stack as testLambdaEnvironmentUpdate # noqa
from stacks_ng.test_lambdas_webhook import Stack as testLambdasWebhook  # noqa
from stacks_ng.test_lambdas_reconciliation import Stack as testLambdasReconciliation  # noqa
from stacks_ng.test_ng_oncall import Stack as testLambdasOnCall # noqa
from stacks_ng.test_ng_codebuild import Stack as testCodeBuildStack # noqa
from stacks_ng.test_ng_waf_log_group import Stack as testLogGroup # noqa
from stacks_ng.test_ng_backup import Stack as testDocumentdbBackup # noqa
from stacks_ng.test_ng_bucket import Stack as testBuckets # noqa
from stacks_ng.test_lambda_power_tuning import Stack as testPowerTunnel # noqa
from stacks_ng.test_ng_ecr import Stack as testECR # noqa
from stacks_ng.test_ng_cloudfront import Stack as testCloudfront # noqa
from stacks_ng.test_ng_buckets_policy import Stack as testBucketsPolicy # noqa
from stacks_ng.test_ng_certificate import Stack as testCertificate # noqa
from stacks_ng.test_ng_roles import Stack as testRoles # noqa
from stacks_ng.test_ng_cross_account_peering import Stack as testVpcPeeringRequester # noqa
from stacks_ng.test_ng_peering_acceptor_route import Stack as testVpcPeeringAcceptor # noqa
from stacks_ng.test_ng_s3_static_webhosting import Stack as StaticRedirectStack # noqa
from stacks_ng.test_ng_kms import Stack as testKmsKey
from stacks_ng.test_ng_notification import FargateSpotNotification # noqa
from stacks_ng.test_ng_dotnet_console_app import DotNetConsoleApp as testDotNetConsoleApp # noqa
from stacks_ng.test_ng_dns_wildcard import testAlb  # noqa
from stacks_ng import test_ng_dns as testDns
from stacks_ng.test_ng_console_app_pipeline import ConsoleAppPipelineStack  # noqa


class test(App):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        env_name = self.get_target_environment_name()
        env_region = self.get_target_environment_region()
        print(f'using environment {env_name} ({env_region})')
        env = self.get_target_environment()

        # Initialize common stacks
        if env_name != "test-master":
            self.initialize_common_stacks(env)

        # Stack initializers based on environment
        stack_initializers = {
            "test-master": self.initialize_master_stacks,
            "test-prod": self.initialize_prod_stacks,
            "test-prod-secondary": self.initialize_prod_secondary_stacks,
            "test-stage": self.initialize_stage_stacks,
            "test-sandbox": self.initialize_sandbox_stacks,
            "test-demo": self.initialize_demo_stacks,
            "test-hotfix-dev": self.initialize_hotfix_dev_stacks,
            "test-qa-new": self.initialize_qa_stacks,
            "test-dev": self.initialize_dev_stacks
        }

        # Initialize environment-specific stacks
        stack_initializers.get(env_name)(env)

        Tags.of(self).add("Owner", "test")
        Tags.of(self).add("ENV", env_name)

    # Common stacks for all environments
    def initialize_common_stacks(self, env):
        testStack(
            self,
            "test-ng",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testNGAdminStack(
            self,
            "test-ng-admin",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testNGServicesApiStack(
            self,
            "test-ng-services-api",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testNGPortal(
            self,
            "test-ng-portal",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testLambdasIngestion(
            self,
            "test-ng-lambdas-ingestion",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasFunding(
            self,
            "test-ng-lambdas-funding",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasEnrichment(
            self,
            "test-ng-lambdas-enrichment",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasCardReloads(
            self,
            "test-ng-lambdas-cardreloads",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasDisbursement(
            self,
            "test-ng-lambdas-disbursement",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasNotification(
            self,
            "test-ng-lambdas-notification",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasWebhook(
            self,
            "test-ng-lambdas-webhook",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasCompliance(
            self,
            "test-ng-lambdas-compliance",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasSequencing(
            self,
            "test-ng-lambdas-sequencing",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasCorrection(
            self,
            "test-ng-lambdas-correction",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testLambdasReconciliation(
            self,
            "test-ng-lambdas-reconciliation",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testSSHTunnel(
            self,
            "test-ng-ssh-tunnel",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testLambdaEnvironmentUpdate(
            self,
            "test-ng-lambda-environment-update",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testLambdasOnCall(
            self,
            "test-ng-oncall",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testLogGroup(
            self,
            "test-ng-waf-log-group",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testBuckets(
            self,
            "test-ng-buckets",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testPowerTunnel(
            self,
            "test-ng-lambda-power-tuning",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testCertificate(
            self,
            "test-ng-certificate",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testRoles(
            self,
            "test-ng-role",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        FargateSpotNotification(
            self,
            "test-ng-notification",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testDotNetConsoleApp(
            self,
            "test-ng-dotnet-console-app",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        testAlb(
            self,
            "test-alb",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        ConsoleAppPipelineStack(
            self,
            "test-ng-console-app-pipeline",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    #  MASTER environment stacks
    def initialize_master_stacks(self, env):
        master_env = Environment(account=self.get_master_account_id())

        master.Stack(
            self,
            'ng-master-account',
            env=master_env,
            metadata=self.get_target_environment_metadata())

        StaticRedirectStack(
            self,
            "test-ng-s3-static-webhosting",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testKmsKey(
            self,
            "test-ng-kms",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )
        testRoles(
            self,
            "test-ng-role",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )
        testDns.Stack(
            self,
            "test-dns",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

    # Common stacks for all LOWER environments
    def initialize_lower_environments_common_stacks(self, env):
        testNGMockStack(
            self,
            "test-ng-jpm-mock-api",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

    # SANDBOX environment stacks here
    def initialize_sandbox_stacks(self, env):
        self.initialize_lower_environments_common_stacks(env)

        testCodeBuildStack(
            self,
            "test-ng-codebuild",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )
        testECR(
            self,
            "test-ng-ecr",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testCloudfront(
            self,
            "test-ng-cloudfront",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testBucketsPolicy(
            self,
            "test-ng-buckets-policy",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        # peering between ng-sandbox and ng-stage
        testVpcPeeringRequester(
            self,
            "test-ng-vpc-peering-sandbox-stage",
            requestor="sandbox",
            acceptor="stage",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        # peering between ng-sandbox and legacy-stage
        testVpcPeeringRequester(
            self,
            "test-ng-vpc-peering-sandbox-legacy-stage",
            requestor="sandbox",
            acceptor="stage",
            legacy_peering=True,
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

    # DEMO environment stacks here
    def initialize_demo_stacks(self, env):
        self.initialize_lower_environments_common_stacks(env)

        testECR(
            self,
            "test-ng-ecr",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testCloudfront(
            self,
            "test-ng-cloudfront",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testBucketsPolicy(
            self,
            "test-ng-buckets-policy",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        # peering between ng-demo and ng-stage
        testVpcPeeringRequester(
            self,
            "test-ng-vpc-peering-demo-stage",
            requestor="demo",
            acceptor="stage",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

        # peering between ng-demo and legacy-stage
        testVpcPeeringRequester(
            self,
            "test-ng-vpc-peering-demo-legacy-stage",
            requestor="demo",
            acceptor="stage",
            legacy_peering=True,
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())

    # Hotfix-Dev environment stacks here
    def initialize_hotfix_dev_stacks(self, env):
        self.initialize_lower_environments_common_stacks(env)

        testECR(
            self,
            "test-ng-ecr",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testCloudfront(
            self,
            "test-ng-cloudfront",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testBucketsPolicy(
            self,
            "test-ng-buckets-policy",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata())
        testNGDocusign(
            self,
            "test-ng-docusign",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )
        testNGDocusignApi(
            self,
            "test-ng-docusign-api",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    # PROD environment stacks
    def initialize_prod_stacks(self, env):
        testDocumentdbBackup(
            self,
            "test-ng-backup",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    # PROD Secondary environment stacks
    def initialize_prod_secondary_stacks(self, env):
        testDocumentdbBackup(
            self,
            "test-ng-backup",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    # STAGE environment stacks
    def initialize_stage_stacks(self, env):
        self.initialize_lower_environments_common_stacks(env)

        testCodeBuildStack(
            self,
            "test-ng-codebuild",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        # Route entries in ng vpc route table for peering with ng-demo
        testVpcPeeringAcceptor(
            self,
            "test-ng-vpc-peering-demo-stage-route",
            requestor="demo",
            acceptor="stage",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        # Route entries in legacy vpc route table for peering with ng-demo
        testVpcPeeringAcceptor(
            self,
            "test-ng-vpc-peering-demo-legacy-stage-route",
            requestor="demo",
            acceptor="stage",
            legacy_peering=True,
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        # Route entries in ng vpc route table for peering with ng-sandbox
        testVpcPeeringAcceptor(
            self,
            "test-ng-vpc-peering-sandbox-stage-route",
            requestor="sandbox",
            acceptor="stage",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        # Route entries in legacy vpc route table for peering with ng-sandbox
        testVpcPeeringAcceptor(
            self,
            "test-ng-vpc-peering-sandbox-legacy-stage-route",
            requestor="sandbox",
            acceptor="stage",
            legacy_peering=True,
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

        testNGDocusign(
            self,
            "test-ng-docusign",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )
        testNGDocusignApi(
            self,
            "test-ng-docusign-api",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    # QA environment stacks here
    def initialize_qa_stacks(self, env):
        self.initialize_lower_environments_common_stacks(env)

        testCodeBuildStack(
            self,
            "test-ng-codebuild",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    # DEV environment stacks
    def initialize_dev_stacks(self, env):
        self.initialize_lower_environments_common_stacks(env)

        testCodeBuildStack(
            self,
            "test-ng-codebuild",
            environment=self.get_target_environment_name(),
            env=env,
            metadata=self.get_target_environment_metadata()
        )

    # Other functions
    def get_default_vpc(self):
        return ec2.Vpc()

    def get_master_account_id(self):
        return self.node.try_get_context("test-master")['id']

    def get_target_environment(self):
        return Environment(
            account=self.get_target_environment_id(),
            region=self.get_target_environment_region()
        )

    def get_target_environment_context(self):
        name = self.get_target_environment_name()
        if name:
            return self.node.try_get_context(name)
        return {}

    def get_target_environment_metadata(self):
        name = self.get_target_environment_name()
        if name:
            return self.node.try_get_context(name)
        return {}

    def get_target_environment_id(self):
        return self.get_target_environment_context().get('id')

    def get_target_environment_name(self):
        return self.node.try_get_context('environment')

    def get_target_environment_region(self):
        return self.get_target_environment_context().get('region')


test().synth()

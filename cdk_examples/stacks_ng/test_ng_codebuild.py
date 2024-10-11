from .modules.codebuild import testCodeBuild
from constructs import Construct
from aws_cdk import (
    Stack as stack,
    aws_iam as iam,
    aws_s3 as s3,
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

        stacks = metadata.get("codebuild")

        artifacts_bucket = s3.Bucket(
            self,
            id="codepipeline-artifacts-bucket-"+environment,
            bucket_name="test-codepipeline-artifacts-bucket-"+environment,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.UNENCRYPTED
        )

        codebuild_role = iam.Role(
            self,
            id='administrator_role_codebuild'+construct_id+environment,
            role_name=('admin_role_codebuild'+construct_id+environment
                       if (environment != "test-prod")
                       else 'admin_role_codebuild'+"role"+construct_id+environment), # noqa
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy
                .from_aws_managed_policy_name('AdministratorAccess')
            ]
        )
        pipeline_role = iam.Role(
            self,
            id='administrator_role_codepipeline'+construct_id+environment,
            role_name=(
                'admin_role_codepipeline'
                + construct_id
                + ("test-qa" if environment == "test-qa-new" else environment) # noqa
                if (environment != "test-prod")
                else 'admin_role_codepipeline'+"role"+construct_id+environment), # noqa
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy
                .from_aws_managed_policy_name('AdministratorAccess')
            ]
        )
        for stack in stacks: # noqa
            testCodeBuild(
                self,
                "stacks-"+stack+"-codebuild",
                environment,
                metadata,
                stacks[stack]["organization"],
                metadata.get("codebuild")[stack]["repo"],
                environment,
                stacks[stack]["cdk_stack_name"],
                stacks[stack]["cdk_version"],
                stacks[stack]["github_branch"],
                metadata.get("id"),
                stacks[stack]["chatbot_topic"],
                stacks[stack]["timeout_duration"],
                stacks[stack]["codestar_connection_arn"],
                codebuild_role,
                pipeline_role,
                artifacts_bucket,
                **kwargs
            )

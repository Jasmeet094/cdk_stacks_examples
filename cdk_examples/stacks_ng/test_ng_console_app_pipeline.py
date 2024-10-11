from constructs import Construct
from aws_cdk import (
    Stack as stack,
    aws_iam as iam,
    aws_s3 as s3,
    aws_codepipeline as codepipeline,
    aws_codepipeline_actions as actions,
    aws_codedeploy as codedeploy,
    aws_codebuild as codebuild,
    aws_sns as sns,
    aws_codestarnotifications as notifications,
    Duration
)


class ConsoleAppPipelineStack(stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        artifacts_bucket = s3.Bucket(
            self,
            id="console-app-artifacts-bucket-"+environment,
            bucket_name="test-ng-console-app-artifacts-bucket-"+environment,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED
        )

        codebuild_role = iam.Role(
            self,
            id='console_app_role_codebuild'+construct_id+environment,
            role_name=('codebuild_role_cicd'+environment),
            assumed_by=iam.ServicePrincipal("codebuild.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy
                .from_aws_managed_policy_name('AdministratorAccess')
            ]
        )

        pipeline_role = iam.Role(
            self,
            id='console_app_role_ci_cd'+construct_id+environment,
            role_name='cicd_dotnet-role'+environment,
            assumed_by=iam.ServicePrincipal("codepipeline.amazonaws.com"),
            managed_policies=[
              iam.ManagedPolicy.from_aws_managed_policy_name(
                  'AdministratorAccess'
              )
            ]
        )

        # Create CodeDeploy service role
        codedeploy_role = iam.Role(
            self,
            id='console_app_role_codedeploy'+construct_id+environment,
            role_name='codedeploy_service_role'+environment,
            assumed_by=iam.ServicePrincipal("codedeploy.amazonaws.com"),
            managed_policies=[
                iam.ManagedPolicy.from_aws_managed_policy_name(
                    'AmazonEC2FullAccess'
                )
            ]
        )

        # Define CodeDeploy application
        codedeploy_app = codedeploy.ServerApplication(
            self, "fx-ng-console-app-"+environment,
            application_name="fx-ng-console-app-"+environment
        )

        # Define CodeDeploy deployment group
        deployment_group = codedeploy.ServerDeploymentGroup(
            self, "DeploymentGroup-"+environment,
            application=codedeploy_app,
            deployment_group_name="deployment-group-console-app-"+environment,
            ec2_instance_tags=codedeploy.InstanceTagSet(
                {"Name": ["fx-ng-dotnet-console-app"]}
            ),
            auto_rollback=codedeploy.AutoRollbackConfig(
                failed_deployment=True
            ),
            role=codedeploy_role
        )

        # Create CodeBuild project
        build_project = codebuild.PipelineProject(
            self,
            "ConsoleAppBuildProject-"+environment,
            project_name="console-app-project-"+environment,
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename(
                "test.ConsoleApp/buildspec.yml"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_7_0,
                compute_type=codebuild.ComputeType.SMALL,
                privileged=False
            ),
            environment_variables={
                "CDK_ENVIRONMENT": codebuild.BuildEnvironmentVariable(
                    value=environment
                ),
                "CDK_STACK_NAME": codebuild.BuildEnvironmentVariable(
                    value="ConsoleAppStack"
                ),
                "CDK_VERSION": codebuild.BuildEnvironmentVariable(
                    value=metadata.get(
                        "dotnet_console_app_pipeline"
                    )["cdk_version"]
                )
            },
            timeout=Duration.hours(1),
            queued_timeout=Duration.hours(8)
        )

        # Create the pipeline
        source_output = codepipeline.Artifact(artifact_name='SourceArtifact')
        build_output = codepipeline.Artifact(artifact_name='BuildArtifact')

        pipeline = codepipeline.Pipeline(
            self,
            "ConsoleAppPipeline-"+environment,
            pipeline_name="console-app-pipeline-"+environment,
            role=pipeline_role,
            artifact_bucket=artifacts_bucket,
            stages=[
                codepipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        actions.CodeStarConnectionsSourceAction(
                            action_name="GitHub_Source",
                            connection_arn=metadata.get(
                                "dotnet_console_app_pipeline"
                            )["connection_arn"],
                            output=source_output,
                            owner="testinc",
                            repo=metadata.get(
                                "dotnet_console_app_pipeline"
                            )["repo"],
                            branch=metadata.get(
                                "dotnet_console_app_pipeline"
                            )["branch"],
                            trigger_on_push=True
                        ),
                    ]
                ),
                codepipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        actions.CodeBuildAction(
                            action_name='Build',
                            project=build_project,
                            input=source_output,
                            outputs=[build_output],
                        )
                    ]
                ),
                codepipeline.StageProps(
                    stage_name='Deploy',
                    actions=[
                        actions.CodeDeployServerDeployAction(
                            action_name="CodeDeploy",
                            input=build_output,
                            deployment_group=deployment_group
                        )
                    ]
                )
            ]
        )

        # Retrieve the SNS topic ARN from the metadata dictionary
        sns_topic_arn = metadata.get(
            "dotnet_console_app_pipeline"
        )["sns_topic"]

        # Reference the existing SNS topic using the retrieved ARN
        sns_topic = sns.Topic.from_topic_arn(
            self, "ExistingSNSTopic", sns_topic_arn
        )

        # Add notification rule for pipeline
        notifications.NotificationRule(
            self,
            "PipelineNotificationRule",
            source=pipeline,
            events=[
                "codepipeline-pipeline-action-execution-failed",
                "codepipeline-pipeline-stage-execution-failed",
                "codepipeline-pipeline-pipeline-execution-succeeded"
            ],
            targets=[sns_topic]
        )

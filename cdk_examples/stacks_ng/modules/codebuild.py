from constructs import Construct
import aws_cdk.aws_codebuild as codebuild
import aws_cdk.aws_codepipeline as pipeline
import aws_cdk.aws_codepipeline_actions as actions
import aws_cdk.aws_codestarnotifications as notifications
from aws_cdk import Duration


class testCodeBuild():

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            environment,
            metadata,
            owner,
            repo,
            cdk_environment,
            cdk_stack_name,
            cdk_version,
            github_branch,
            account_id,
            chatbot_topic,
            timeout_duration,
            codestar_connection_arn,
            codebuild_role,
            pipeline_role,
            artifacts_bucket,
            **kwargs):

        source_output = pipeline.Artifact(artifact_name='source')

        code_build = codebuild.PipelineProject(
            scope,
            construct_id+"-Project-"+environment,
            project_name=construct_id+"-"+environment,
            role=codebuild_role,
            build_spec=codebuild.BuildSpec.from_source_filename(
                "buildspec.yml"
            ),
            environment=codebuild.BuildEnvironment(
                build_image=codebuild.LinuxBuildImage.STANDARD_5_0,
                privileged=True
            ),
            environment_variables={
                "CDK_ENVIRONMENT": codebuild.BuildEnvironmentVariable(
                    value=cdk_environment
                ),
                "CDK_STACK_NAME": codebuild.BuildEnvironmentVariable(
                    value=cdk_stack_name
                ),
                "CDK_VERSION": codebuild.BuildEnvironmentVariable(
                    value=cdk_version
                )
            },
            timeout=Duration.hours(timeout_duration),
        )

        cfn_codebuild = code_build.node.default_child
        cfn_codebuild.add_override(
            "Properties.SourceVersion",
            github_branch
        )

        rule = notifications.NotificationRule(
            scope,
            construct_id+"-rule-"+environment,
            notification_rule_name=(construct_id+"-rule-"+environment
                                    if (environment != "test-prod-secondary")  # noqa
                                    else construct_id+"-"+environment),
            source=code_build,
            detail_type=notifications.DetailType.BASIC,
            events=[
                "codebuild-project-build-state-succeeded",
                "codebuild-project-build-state-failed"
            ],
        )

        cfn_notification_rule = rule.node.default_child
        cfn_notification_rule.add_override(
            "Properties.Targets",
            [dict({
                "TargetAddress": "arn:aws:chatbot::" +
                account_id+":chat-configuration/slack-channel/" +
                chatbot_topic,
                "TargetType": "AWSChatbotSlack"
            })]
        )

        pipeline.Pipeline(
            scope,
            construct_id+"-Pipeline-"+environment,
            role=pipeline_role,
            pipeline_name=construct_id+"-"+environment,
            artifact_bucket=artifacts_bucket,
            pipeline_type=pipeline.PipelineType.V2,
            stages=[
                pipeline.StageProps(
                    stage_name='Source',
                    actions=[
                        actions.CodeStarConnectionsSourceAction(
                            action_name="GitHub_Source",
                            connection_arn=codestar_connection_arn,
                            output=source_output,
                            owner=owner,
                            repo=repo,
                            branch=github_branch
                        ),
                    ]
                ),
                pipeline.StageProps(
                    stage_name='Build',
                    actions=[
                        actions.CodeBuildAction(
                            action_name='Build',
                            input=source_output,
                            project=code_build,
                            run_order=1,
                        )
                    ]
                )
            ]

        )

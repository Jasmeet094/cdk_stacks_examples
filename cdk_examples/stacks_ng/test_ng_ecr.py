from aws_cdk import (
    aws_ecr as ecr,
    Stack as stack,
    CfnOutput
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

        repo_names = metadata.get('ecr_repos', [])
        for repo_name in repo_names:
            self.create_ecr_repository(repo_name)

    def create_ecr_repository(self, repo_name):

        repository = ecr.Repository(
            self,
            f"Id{repo_name}",
            repository_name=repo_name
        )

        CfnOutput(
            self,
            f"Output{repo_name}",
            value=repository.repository_arn,
            export_name=f'RepoArn{repo_name}'
        )

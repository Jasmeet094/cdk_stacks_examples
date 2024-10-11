import aws_cdk as core
import aws_cdk.assertions as assertions

from stacks_ng.stacks_ng_stack import StacksNgStack


def test_sqs_queue_created():
    app = core.App()
    stack = StacksNgStack(app, "stacks-ng")
    template = assertions.Template.from_stack(stack)

    template.has_resource_properties("AWS::SQS::Queue", {
        "VisibilityTimeout": 300
    })

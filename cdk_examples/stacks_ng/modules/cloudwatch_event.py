from aws_cdk import (
    aws_lambda as lambda_,
    aws_events as events,
    Duration
)


class CWEventRuleCron:
    def __init__(
            self,
            scope,
            id,
            environment,
            enabled,
            lambda_arn,
            lambda_name,
            rate_time,
            rule_name,
            **kwargs):

        self.event_rule = events.Rule(
            scope,
            id + "-" + environment,
            enabled=enabled,
            rule_name=rule_name,
            description="Cloudwatch event rule for NextGen lambda",
            schedule=events.Schedule.rate(
                duration=Duration.minutes(rate_time)
            )
        )

        self.cfn_event_rule = self.event_rule.node.children[0]
        self.cfn_event_rule.add_override(
            "Properties.Targets",
            [dict({
                "Arn": lambda_arn,
                "Id": lambda_name
            })]
        )

        self.lambda_invoke = lambda_.CfnPermission(
            scope,
            id + "-" + "invoke" + environment,
            action="lambda:InvokeFunction",
            function_name=lambda_name,
            principal="events.amazonaws.com",
            source_arn=self.event_rule.rule_arn
        )

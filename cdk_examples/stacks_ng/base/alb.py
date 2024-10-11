from aws_cdk import (
    aws_ec2 as ec2,
    aws_certificatemanager as acm,
    aws_elasticloadbalancingv2 as elbv2,
    aws_logs as logs,
    aws_wafv2 as waf,
    Fn
)
from aws_cdk.aws_elasticloadbalancingv2 import SslPolicy
import json


class ApplicationLoadBalancer:

    def excluded_rules_list(self, id):
        excluded_rules = [
            waf.CfnWebACL.ExcludedRuleProperty(
                name="SizeRestrictions_BODY")
        ]
        if id == "test-ng-portal":
            excluded_rules.append(
                waf.CfnWebACL.ExcludedRuleProperty(
                    name="CrossSiteScripting_BODY")
            )
        return excluded_rules

    def create_ip_set_rule(self, ip_set_arn, priority, rule_name):
        return waf.CfnWebACL.RuleProperty(
            name=rule_name,
            priority=priority,
            statement=waf.CfnWebACL.StatementProperty(
                ip_set_reference_statement={
                    "arn": ip_set_arn
                }
            ),
            visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                sampled_requests_enabled=True,
                cloud_watch_metrics_enabled=True,
                metric_name=rule_name,
            ),
            action=waf.CfnWebACL.RuleActionProperty(
                block=waf.CfnWebACL.BlockActionProperty(
                    custom_response=waf.CfnWebACL.CustomResponseProperty(
                        response_code=403
                    )
                )
            )
        )

    def create_body_size_limit_rule(self, name, priority,
                                    comparison_operator,
                                    size_limit, search_string):
        return waf.CfnWebACL.RuleProperty(
                        name=name,
                        priority=priority,
                        statement=waf.CfnWebACL.StatementProperty(
                            and_statement=waf.CfnWebACL.AndStatementProperty(
                                statements=[
                                    waf.CfnWebACL.StatementProperty(
                                        size_constraint_statement=waf.CfnWebACL.SizeConstraintStatementProperty(  # noqa
                                            comparison_operator=comparison_operator, # noqa
                                            field_to_match=waf.CfnWebACL.FieldToMatchProperty( # noqa
                                                body={"OversizeHandling": "CONTINUE"} # noqa
                                            ),
                                            size=size_limit,
                                            text_transformations=[
                                                waf.CfnWebACL.TextTransformationProperty(priority=0, type="NONE")  # noqa
                                            ]
                                        )
                                    ),
                                    waf.CfnWebACL.StatementProperty(
                                        byte_match_statement=waf.CfnWebACL.ByteMatchStatementProperty(  # noqa
                                            search_string=search_string,
                                            positional_constraint="CONTAINS",
                                            field_to_match=waf.CfnWebACL.FieldToMatchProperty(uri_path={}),  # noqa
                                            text_transformations=[
                                                waf.CfnWebACL.TextTransformationProperty(priority=0, type="NONE")  # noqa
                                            ]
                                        )
                                    )
                                ]
                            ),
                        ),
                        visibility_config=waf.CfnWebACL.VisibilityConfigProperty( # noqa
                            sampled_requests_enabled=True,
                            cloud_watch_metrics_enabled=True,
                            metric_name=name,
                        ),
                        action=waf.CfnWebACL.RuleActionProperty(
                            allow=waf.CfnWebACL.AllowActionProperty()
                        )
                    )

    def __init__(self, scope, id, environment, vpc, metadata,
                 public, **kwargs):

        if public:
            vpc_subnets = kwargs.get(
                "vpc_subnets",
                ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC))
        else:
            vpc_subnets = kwargs.get(
                "vpc_subnets",
                ec2.SubnetSelection(
                    subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)
                )

        self.alb = elbv2.ApplicationLoadBalancer(
            scope,
            "ALB-" + id + "-" + environment,
            vpc=vpc,
            vpc_subnets=vpc_subnets,
            internet_facing=public
        )

        self.alb.set_attribute(
            key="routing.http.drop_invalid_header_fields.enabled",
            value="true")

        self.http_listener = self.alb.add_listener(
            "http-" + id + "-" + environment,
            port=80,
            protocol=elbv2.ApplicationProtocol.HTTP,
            default_action=elbv2.ListenerAction.redirect(
                host="#{host}",
                path="/#{path}",
                permanent=True,
                port="443",
                protocol="HTTPS",
                query="#{query}"
            )
        )
        certificates = []

        for cert in metadata.get("certificates", []):
            certificates.append(
                acm.Certificate.from_certificate_arn(
                    scope,
                    "cert-" + id +
                    str(metadata.get("certificates").index(cert)),
                    cert))

        self.https_listener = self.alb.add_listener(
            "https-" + id + "-" + environment,
            port=443,
            protocol=elbv2.ApplicationProtocol.HTTPS,
            certificates=certificates,
            default_action=elbv2.ListenerAction.fixed_response(
                status_code=404,
                content_type="text/plain",
                message_body="default"
            ),
            ssl_policy=SslPolicy.TLS12
        )

        if public:
            ap_ip_set_arn = Fn.import_value('armorpoint-block-ip-set-arn')  # noqa
            ap_ip_set_arn2 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet2')  # noqa
            ap_ip_set_arn3 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet3')  # noqa
            ap_ip_set_arn4 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet4')  # noqa
            ap_ip_set_arn5 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet5')  # noqa
            ap_ip_set_arn6 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet6')  # noqa
            ap_ip_set_arn7 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet7')  # noqa
            ap_ip_set_arn8 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet8')  # noqa
            ap_ip_set_arn9 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet9')  # noqa
            ap_ip_set_arn10 = Fn.import_value('armorpoint-block-ip-set-arnArmorPointBlockIPSet10')  # noqa
            oncall_ip_set_arn = Fn.import_value('oncall-ip-set-arn')

            acl_rules = [
                    waf.CfnWebACL.RuleProperty(
                        name="AWS-AWSManagedRulesAmazonIpReputationList",
                        priority=0,
                        statement=waf.CfnWebACL.StatementProperty(
                            managed_rule_group_statement=waf
                            .CfnWebACL.ManagedRuleGroupStatementProperty(
                                vendor_name="AWS",
                                name="AWSManagedRulesAmazonIpReputationList"
                            )
                        ),
                        override_action=waf.CfnWebACL.OverrideActionProperty(
                            none={}
                        ),
                        visibility_config=waf
                        .CfnWebACL.VisibilityConfigProperty(
                            sampled_requests_enabled=True,
                            cloud_watch_metrics_enabled=True,
                            metric_name="AWS-AWSManagedRulesAmazonIpReputationList",  # noqa
                        ),
                    ),
                    self.create_ip_set_rule(ap_ip_set_arn, 1, "ArmorPointBlockIPSet"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn2, 2, "ArmorPointBlockIPSet2"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn3, 3, "ArmorPointBlockIPSet3"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn4, 4, "ArmorPointBlockIPSet4"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn5, 5, "ArmorPointBlockIPSet5"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn6, 6, "ArmorPointBlockIPSet6"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn7, 7, "ArmorPointBlockIPSet7"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn8, 8, "ArmorPointBlockIPSet8"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn9, 9, "ArmorPointBlockIPSet9"), # noqa
                    self.create_ip_set_rule(ap_ip_set_arn10, 10, "ArmorPointBlockIPSet10"), # noqa
                    self.create_ip_set_rule(oncall_ip_set_arn, 11, "BlockIPSet"), # noqa
                    waf.CfnWebACL.RuleProperty(
                        name="BlockCountryCodes-"+environment,
                        priority=12,
                        statement=waf.CfnWebACL.StatementProperty(
                            geo_match_statement=waf.CfnWebACL.GeoMatchStatementProperty( # noqa
                                country_codes=metadata.get("waf_acl")[
                                    "countries_list"
                                ]
                            )
                        ),
                        visibility_config=waf
                        .CfnWebACL.VisibilityConfigProperty(
                            sampled_requests_enabled=True,
                            cloud_watch_metrics_enabled=True,
                            metric_name="BlockCountryCodes-"+environment,  # noqa
                        ),
                        action=waf.CfnWebACL.RuleActionProperty(
                            block=waf.CfnWebACL.BlockActionProperty(
                                custom_response=waf.CfnWebACL.
                                CustomResponseProperty(
                                    response_code=403
                                )
                            )
                        )
                    ),

                    waf.CfnWebACL.RuleProperty(
                        name="AWS-AWSManagedRulesCommonRuleSet",
                        priority=50,
                        statement=waf.CfnWebACL.StatementProperty(
                            managed_rule_group_statement=waf
                            .CfnWebACL.ManagedRuleGroupStatementProperty(
                                vendor_name="AWS",
                                name="AWSManagedRulesCommonRuleSet",
                                excluded_rules=self.excluded_rules_list(id)
                            )
                        ),
                        override_action=waf.CfnWebACL.OverrideActionProperty(
                            none={}
                        ),
                        visibility_config=waf
                        .CfnWebACL.VisibilityConfigProperty(
                            sampled_requests_enabled=True,
                            cloud_watch_metrics_enabled=True,
                            metric_name="AWS-AWSManagedRulesCommonRuleSet",
                        ),
                    ),
            ]

            # Append Body size limit rules to test-platform only
            if id in ["test-ng-admin"]:
                acl_rules.append(self.create_body_size_limit_rule("BodySizeLimit-SupplierValidateFile", # noqa
                                                                  21, "LE", 400000, "/Suppliers/validatefile")) # noqa
                acl_rules.append(self.create_body_size_limit_rule("BodySizeLimit-SupplierFileUpload", # noqa
                                                                  22, "LE", 5000000, "/Suppliers/uploadfile")) # noqa

            self.webacl = waf.CfnWebACL(
                scope,
                "WAF-" + id + "-" + environment,
                default_action=waf.CfnWebACL.DefaultActionProperty(allow={}),
                scope="REGIONAL",
                visibility_config=waf.CfnWebACL.VisibilityConfigProperty(
                    cloud_watch_metrics_enabled=True,
                    metric_name="WAF",
                    sampled_requests_enabled=True,
                ),
                rules=acl_rules
            )

            self.cfn_log_group = logs.CfnLogGroup(
                scope,
                "aws-waf-logs-"+id+"-"+environment,
                log_group_name="aws-waf-logs-"+id+"-"+environment,
                retention_in_days=14
            )

            self.logging_filter = '''
            {
                "DefaultBehavior": "DROP",
                "Filters": [
                    {
                    "Behavior": "KEEP",
                    "Conditions": [
                        {
                        "ActionCondition": {
                            "Action": "BLOCK"
                        }
                        }
                    ],
                    "Requirement": "MEETS_ANY"
                    },
                    {
                    "Behavior": "DROP",
                    "Conditions": [
                        {
                        "ActionCondition": {
                            "Action": "ALLOW"
                        }
                        },
                        {
                        "ActionCondition": {
                            "Action": "COUNT"
                        }
                        },
                        {
                        "ActionCondition": {
                            "Action": "CAPTCHA"
                        }
                        }
                    ],
                    "Requirement": "MEETS_ANY"
                    }
                ]
            }'''

            waf.CfnLoggingConfiguration(
                scope,
                id+"-loggingconfiguration-"+environment,
                log_destination_configs=[Fn.import_value(
                    "test-ng-waf-log-group-arn" + "-" + environment
                    )
                ],
                resource_arn=self.webacl.attr_arn,
                logging_filter=json.loads(self.logging_filter)
            )

            waf.CfnWebACLAssociation(
                scope,
                "WAFassoc-" + id + "-" + environment,
                resource_arn=self.alb.load_balancer_arn,
                web_acl_arn=self.webacl.attr_arn
            )

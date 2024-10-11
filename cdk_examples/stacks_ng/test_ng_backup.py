from aws_cdk import (
    aws_iam as iam,
    aws_sns as sns,
    aws_backup as backup,
)
import json

from constructs import Construct
from aws_cdk import Stack as stack


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

        self.sns_topic = sns.CfnTopic(
            self,
            "backup-sns-"+id+"-"+environment,
            topic_name="backup-sns-"+id+"-"+environment,
            display_name="backup-sns-"+id+"-"+environment,
        )
        self.sns_topic_arn = self.sns_topic.ref
        self.sns_topic_policy_json = '''
        {
            "Version": "2008-10-17",
            "Statement": [
                {
                "Sid": "AllowServices",
                "Effect": "Allow",
                "Principal": {
                    "Service": [
                    "events.amazonaws.com",
                    "backup.amazonaws.com"
                    ]
                },
                "Action": "sns:Publish",
                "Resource": "TO_REPLACE"
                }
            ]
        }
        '''.replace('TO_REPLACE', self.sns_topic_arn)
        self.sns_topic_policy = sns.CfnTopicPolicy(
            self,
            "backup-sns-policy-"+id+"-"+environment,
            policy_document=json.loads(self.sns_topic_policy_json),
            topics=[self.sns_topic.ref]
        )
        self.backup_vault = backup.CfnBackupVault(
            self,
            "backup-vault-"+id+"-"+environment,
            backup_vault_name="backup-vault-"+id+"-"+environment
                              if environment == "test-prod"
                              else "hourly-"+id+"-"+environment,
            notifications=backup.CfnBackupVault.NotificationObjectTypeProperty(
                backup_vault_events=[
                    "BACKUP_JOB_SUCCESSFUL",
                    "BACKUP_JOB_FAILED"
                ],
                sns_topic_arn=self.sns_topic.ref
            )
        )
        self.backup_vault_daily = backup.CfnBackupVault(
            self,
            "backup-vault-daily-"+id+"-"+environment,
            backup_vault_name="backup-vault-daily-"+id+"-"+environment
                              if environment == "test-prod"
                              else "daily-"+id+"-"+environment,
            notifications=backup.CfnBackupVault.NotificationObjectTypeProperty(
                backup_vault_events=[
                    "BACKUP_JOB_SUCCESSFUL",
                    "BACKUP_JOB_FAILED"
                ],
                sns_topic_arn=self.sns_topic.ref
            )
        )
        self.backup_vault_weekly = backup.CfnBackupVault(
            self,
            "backup-vault-weekly-"+id+"-"+environment,
            backup_vault_name="backup-weekly-"+id+"-"+environment
                              if environment == "test-prod"
                              else "weekly-"+id+"-"+environment,
            notifications=backup.CfnBackupVault.NotificationObjectTypeProperty(
                backup_vault_events=[
                    "BACKUP_JOB_SUCCESSFUL",
                    "BACKUP_JOB_FAILED"
                ],
                sns_topic_arn=self.sns_topic.ref
            )
        )
        self.backup_vault_monthly = backup.CfnBackupVault(
            self,
            "backup-vault-monthly-"+id+"-"+environment,
            backup_vault_name="backup-monthly-"+id+"-"+environment
                              if environment == "test-prod"
                              else "monthly-"+id+"-"+environment,
            notifications=backup.CfnBackupVault.NotificationObjectTypeProperty(
                backup_vault_events=[
                    "BACKUP_JOB_SUCCESSFUL",
                    "BACKUP_JOB_FAILED"
                ],
                sns_topic_arn=self.sns_topic.ref
            )
        )
        self.backup_vault_yearly = backup.CfnBackupVault(
            self,
            "backup-vault-yearly-"+id+"-"+environment,
            backup_vault_name="backup-yearly-"+id+"-"+environment
                              if environment == "test-prod"
                              else "yearly-"+id+"-"+environment,
            notifications=backup.CfnBackupVault.NotificationObjectTypeProperty(
                backup_vault_events=[
                    "BACKUP_JOB_SUCCESSFUL",
                    "BACKUP_JOB_FAILED"
                ],
                sns_topic_arn=self.sns_topic.ref
            )
        )
        if environment == "test-prod":
            days_for_hourly = float(self.node.try_get_context('test-prod')
                                    ["backup_documentdb"]
                                    ["hourly_rule_retention_days"])
            days_for_daily = float(self.node.try_get_context('test-prod')
                                   ["backup_documentdb"]
                                   ["daily_rule_retention_days"])
            days_for_weekly = float(self.node.try_get_context('test-prod')
                                    ["backup_documentdb"]
                                    ["weekly_rule_retention_days"])
            days_for_monthly = float(self.node.try_get_context('test-prod')
                                     ["backup_documentdb"]
                                     ["monthly_rule_retention_days"])
            days_for_yearly_cold_storage = float(self.node.try_get_context
                                                 ('test-prod')
                                                 ["backup_documentdb"]
                                                 ["yearly_rule_cold_storage_days"]) # noqa
            days_for_monthly_cold_storage = float(
                self.node.try_get_context
                ('test-prod')
                ["backup_documentdb"]
                ["monthly_rule_cold_storage_days"]
            )
            self.backup_plan = backup.CfnBackupPlan(
                self,
                "backup-plan-"+id+"-"+environment,
                backup_plan=backup.CfnBackupPlan.BackupPlanResourceTypeProperty
                (
                    backup_plan_name="backup-plan-"+id+"-"+environment,
                    backup_plan_rule=[
                        backup.CfnBackupPlan.BackupRuleResourceTypeProperty(
                            rule_name="backup-rule-hourly-"+id+"-"+environment,
                            target_backup_vault=self.backup_vault.ref,
                            start_window_minutes=60,
                            completion_window_minutes=1440,
                            schedule_expression=self.node.try_get_context
                            ('test-prod')
                            ["backup_documentdb"]
                            ["cron_schedule_hourly"],
                            lifecycle=backup
                            .CfnBackupPlan
                            .LifecycleResourceTypeProperty(
                                delete_after_days=days_for_hourly
                            ),
                            copy_actions=[
                                backup.CfnBackupPlan.CopyActionResourceTypeProperty( # noqa
                                    destination_backup_vault_arn="arn:aws:backup:" + # noqa
                                    self.node.try_get_context
                                    ('test-prod-secondary')
                                    ["region"]
                                    + ":" + self.node.try_get_context
                                    ('test-prod-secondary')["id"]
                                    + ":backup-vault:hourly-"
                                    + id+"-test-prod-secondary",
                                    lifecycle=backup.CfnBackupPlan.LifecycleResourceTypeProperty( # noqa
                                        delete_after_days=days_for_hourly
                                        )
                                        )]
                        ),
                        backup.CfnBackupPlan.BackupRuleResourceTypeProperty(
                            rule_name="backup-rule-daily-"+id+"-"+environment,
                            target_backup_vault=self.backup_vault_daily.ref,
                            start_window_minutes=60,
                            completion_window_minutes=1440,
                            schedule_expression=self.node.try_get_context
                            ('test-prod')
                            ["backup_documentdb"]
                            ["cron_schedule_daily"],
                            lifecycle=backup
                            .CfnBackupPlan
                            .LifecycleResourceTypeProperty(
                                delete_after_days=days_for_daily
                            ),
                            copy_actions=[
                                backup.CfnBackupPlan.CopyActionResourceTypeProperty( # noqa
                                    destination_backup_vault_arn="arn:aws:backup:" + # noqa
                                    self.node.try_get_context
                                    ('test-prod-secondary')
                                    ["region"]+":"
                                    + self.node.try_get_context
                                    ('test-prod-secondary')["id"]
                                    + ":backup-vault:daily-"
                                    + id+"-test-prod-secondary",
                                    lifecycle=backup.CfnBackupPlan.LifecycleResourceTypeProperty( # noqa
                                        delete_after_days=days_for_daily
                                        )
                                    )]
                        ),
                        backup.CfnBackupPlan.BackupRuleResourceTypeProperty(
                            rule_name="backup-rule-weekly-"+id+"-"+environment,
                            target_backup_vault=self.backup_vault_weekly.ref,
                            start_window_minutes=60,
                            completion_window_minutes=1440,
                            schedule_expression=self.node.try_get_context
                            ('test-prod')
                            ["backup_documentdb"]
                            ["cron_schedule_weekly"],
                            lifecycle=backup
                            .CfnBackupPlan
                            .LifecycleResourceTypeProperty(
                                delete_after_days=days_for_weekly
                            ),
                            copy_actions=[
                                backup.CfnBackupPlan.CopyActionResourceTypeProperty( # noqa
                                    destination_backup_vault_arn="arn:aws:backup:" + # noqa
                                    self.node.try_get_context
                                    ('test-prod-secondary')["region"]
                                    + ":" + self.node.try_get_context
                                    ('test-prod-secondary')["id"]
                                    + ":backup-vault:weekly-"
                                    + id+"-test-prod-secondary",
                                    lifecycle=backup.CfnBackupPlan.LifecycleResourceTypeProperty( # noqa
                                        delete_after_days=days_for_weekly
                                        )
                                    )]
                        ),
                        backup.CfnBackupPlan.BackupRuleResourceTypeProperty(
                            rule_name="backup-rule-monthly-"+id+"-"
                            + environment,
                            target_backup_vault=self.backup_vault_monthly.ref,
                            start_window_minutes=60,
                            completion_window_minutes=1440,
                            schedule_expression=self.node.try_get_context
                            ('test-prod')
                            ["backup_documentdb"]
                            ["cron_schedule_monthly"],
                            lifecycle=backup
                            .CfnBackupPlan
                            .LifecycleResourceTypeProperty(
                                delete_after_days=days_for_monthly,
                                move_to_cold_storage_after_days=days_for_monthly_cold_storage # noqa
                            ),
                            copy_actions=[
                                backup.CfnBackupPlan.CopyActionResourceTypeProperty( # noqa
                                    destination_backup_vault_arn="arn:aws:backup:" + # noqa
                                    self.node.try_get_context
                                    ('test-prod-secondary')["region"]
                                    + ":" + self.node.try_get_context
                                    ('test-prod-secondary')["id"]
                                    + ":backup-vault:monthly-"
                                    + id+"-test-prod-secondary",
                                    lifecycle=backup.CfnBackupPlan.LifecycleResourceTypeProperty( # noqa
                                        delete_after_days=days_for_monthly
                                        )
                                    )]
                        ),
                        backup.CfnBackupPlan.BackupRuleResourceTypeProperty(
                            rule_name="backup-rule-yearly-"+id+"-"+environment,
                            target_backup_vault=self.backup_vault_yearly.ref,
                            start_window_minutes=60,
                            completion_window_minutes=1440,
                            schedule_expression=self.node.try_get_context
                            ('test-prod')
                            ["backup_documentdb"]
                            ["cron_schedule_yearly"],
                            lifecycle=backup
                            .CfnBackupPlan
                            .LifecycleResourceTypeProperty
                            (
                                move_to_cold_storage_after_days=days_for_yearly_cold_storage # noqa
                            ),
                            copy_actions=[
                                backup.CfnBackupPlan.CopyActionResourceTypeProperty( # noqa
                                    destination_backup_vault_arn="arn:aws:backup:" + # noqa
                                    self.node.try_get_context
                                    ('test-prod-secondary')["region"]
                                    + ":" + self.node.try_get_context
                                    ('test-prod-secondary')["id"]
                                    + ":backup-vault:yearly-"
                                    + id+"-test-prod-secondary",
                                    lifecycle=backup.CfnBackupPlan.LifecycleResourceTypeProperty( # noqa
                                        move_to_cold_storage_after_days=days_for_yearly_cold_storage # noqa
                                        )
                                    )]
                        )
                    ]
                )
            )
            self.backup_role = iam.Role(
                self,
                id,
                assumed_by=iam.ServicePrincipal("backup.amazonaws.com"),
                description="IAM role for AWS Backup"
            )
            self.backup_role.add_managed_policy(
                policy=iam.ManagedPolicy.from_aws_managed_policy_name(
                    "service-role/AWSBackupServiceRolePolicyForBackup"
                )
            )
            self.backup_selection = backup.CfnBackupSelection(
                self,
                "backup-selection-"+id+"-"+environment,
                backup_plan_id=self.backup_plan.ref,
                backup_selection=backup
                .CfnBackupSelection
                .BackupSelectionResourceTypeProperty(
                        iam_role_arn=self.backup_role.role_arn,
                        selection_name="backup-selection-"+id+"-"+environment,
                        resources=[self.node.try_get_context
                                   ('test-prod')
                                   ["backup_documentdb"]
                                   ["docdb_arn"]]
                        )
                )

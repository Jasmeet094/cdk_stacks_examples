from .modules.lambda_event_bridge import LambdaEnvironmentUpdate
from constructs import Construct
from aws_cdk import (
  Stack as stack,
  Fn
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

        self.scope = scope
        self.construct_id = construct_id
        function_arn_list = []

        function_arn_list.append(
          Fn.import_value(
            "test-notification-set-function-arn" + "-" + environment
            )
          )

        function_arn_list.append(
          Fn.import_value(
            "test-timing-monitor-function-arn" + "-" + environment
            )
          )

        function_arn_list.append(
          Fn.import_value(
            "test-compliance-scanner-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-compliance-timing-monitor-function-arn" +
            "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-correction-payments-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-correction-timing-monitor-function-arn" +
            "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-disbursement-batches-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-disbursement-payments-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-disbursement-timing-monitor-function-arn" +
            "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-funding-requests-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-funding-payments-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-funding-timing-monitor-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-ingestion-invoice-file-movement-function-arn" +
            "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-ingestion-invoice-sets-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-ingestion-jpm-cbm-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-ingestion-timing-monitor-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-sequencer-function-arn" + "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-sequencing-timing-monitor-function-arn" +
            "-" + environment
            )
          )
        function_arn_list.append(
          Fn.import_value(
            "test-webhook-payment-status-notification-function-arn" +
            "-" + environment
            )
          )
        function_arn_list.append(
            Fn.import_value(
                "test-enrichment-function-arn" +
                "-" + environment
            )
        )
        function_arn_list.append(
            Fn.import_value(
                "test-reconciliation-end-of-day-function-arn" +
                "-" + environment
            )
        )

        lambda_function_names = str(Fn.import_value(
            "test-notification-set-function-name-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-timing-monitor-function-name" + "-" + environment))

        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-compliance-scanner-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-compliance-timing-monitor-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-correction-payments-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-correction-timing-monitor-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-disbursement-batches-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-disbursement-payments-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-disbursement-timing-monitor-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-funding-requests-function-name" + "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-funding-payments-function-name" + "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-funding-timing-monitor-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-ingestion-invoice-file-movement-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-ingestion-invoice-sets-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-ingestion-jpm-cbm-function-name" + "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-ingestion-timing-monitor-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-sequencer-function-name" + "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-sequencing-timing-monitor-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-webhook-payment-status-notification-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-enrichment-function-name" +
                "-" + environment))
        lambda_function_names = lambda_function_names + "," \
            + str(Fn.import_value(
                "test-reconciliation-end-of-day-function-name" +
                "-" + environment))

        self.lambda_env_update = LambdaEnvironmentUpdate(
            self,
            "test-lambda-env-update",
            region=metadata.get("region"),
            account_id=metadata.get("id"),
            environment=environment,
            event_enabled=metadata.get("env_update_lambda")[
              "event_rules"]["enabled"],
            secret_name=metadata.get("env_update_lambda")["secret_name"],
            function_arn_list=function_arn_list,
            function_names=lambda_function_names,
            assets_path="assets/lambda_env_update_lambda",
            lambda_timeout=metadata.get("env_update_lambda")["timeout"]
          )

import boto3
import json
import logging
import os
import sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def disable_lambda_triggers():
    client = boto3.client('lambda')

    response = client.list_functions()

    lambda_sqs_list = []
    for func in response['Functions']:
        # All the Nextgen lambda's desciption includes keyword - NextGen
        if 'NextGen' in func['Description']:
            event_source_mappings = client.list_event_source_mappings(
                FunctionName=func['FunctionName'])['EventSourceMappings']
            for EventSourceArn in event_source_mappings:
                event_source_arn = EventSourceArn['EventSourceArn']

                # Shortlist lambdas which have trigger sqs attached with them
                if "arn:aws:sqs" in event_source_arn:
                    lambda_sqs_list.append(func['FunctionName'])

    for lambda_name in lambda_sqs_list:
        try:
            # Disable triggers based on the event source mappings
            event_source_mappings = client.list_event_source_mappings(
                FunctionName=lambda_name)['EventSourceMappings']
            for mapping in event_source_mappings:
                mapping_id = mapping['UUID']
                client.update_event_source_mapping(
                    UUID=mapping_id, Enabled=False)

            print(f"Triggers disabled for Lambda function: {lambda_name}")

        except client.exceptions.ResourceNotFoundException:
            print(f"Lambda function not found: {lambda_name}")
        except Exception as e:
            print(f"Error disabling triggers for {lambda_name}: {str(e)}")


def disable_cloudwatch_rules():
    client = boto3.client('events')

    lambda_cw_event_list = []
    event_rule_list = client.list_rules()

    for event_rule in event_rule_list['Rules']:
        # check if parameter Description exist or not
        if 'Description' in event_rule:
            if 'NextGen' in event_rule["Description"]:
                lambda_cw_event_list.append(event_rule['Name'])

    for rule_name in lambda_cw_event_list:
        try:
            # Disable CloudWatch rule
            client.disable_rule(Name=rule_name)

            print(f"CloudWatch rule disabled: {rule_name}")

        except client.exceptions.ResourceNotFoundException:
            print(f"CloudWatch rule not found: {rule_name}")
        except Exception as e:
            print(f"Error disabling CloudWatch rule {rule_name}: {str(e)}")


def lambda_handler(event, context):
    try:
        # Stop ECS Services
        client_ecs = boto3.client('ecs')
        client_autoscale = boto3.client('application-autoscaling')

        cluster_response = client_ecs.list_clusters()
        clusterlist = cluster_response['clusterArns']
        for clusterArn in clusterlist:
            response = client_ecs.list_services(
                    cluster=clusterArn
                )
            ConditionString = True
            while ConditionString:
                for services in range(len(response['serviceArns'])):
                    service_arn = response['serviceArns'][services]

                    # Cluster Name
                    cluster_data = client_ecs.describe_clusters(
                        clusters=[clusterArn]
                        )
                    cluster_name = cluster_data['clusters'][0]['clusterName']

                    # Service Name
                    service_data = client_ecs.describe_services(
                        cluster=clusterArn,
                        services=[service_arn]
                        )
                    service_name = service_data['services'][0]['serviceName']

                    # update Min/Max
                    client_autoscale.register_scalable_target(
                        ServiceNamespace='ecs',
                        ResourceId=f'service/{cluster_name}/{service_name}',
                        ScalableDimension='ecs:service:DesiredCount',
                        MinCapacity=0,
                        MaxCapacity=0
                    )
                if "nextToken" in response:
                    response = client_ecs.list_services(
                        cluster=clusterArn,
                        nextToken=response['nextToken']
                    )
                else:
                    ConditionString = False

        # Stop RDS Cluster
        client_rds = boto3.client('rds')
        rds_clusters = os.environ['rds_cluster_identifier']\
            .strip("[]").replace(" ", "").replace("'", "")

        if rds_clusters:
            rdsclusterlist = list(rds_clusters.split(","))
            for cluster in rdsclusterlist:
                client_rds.stop_db_cluster(
                    DBClusterIdentifier=cluster
                )

        # Stop Docdb Cluster
        client_docdb = boto3.client('docdb')

        docdb_cluster_identifier = os.environ['docdb_cluster_identifier']
        if docdb_cluster_identifier:
            client_docdb.stop_db_cluster(
                DBClusterIdentifier=docdb_cluster_identifier
            )

        # Stop EC2 Instances
        running_instances_list = []
        ec2 = boto3.client('ec2')
        ec2_response = ec2.describe_instances(
            Filters=[
                {
                    'Name': 'instance-state-name',
                    'Values': ["running"]
                }
                ])

        if ec2_response['Reservations']:
            for reservations in ec2_response['Reservations']:
                for instances in reservations['Instances']:
                    running_instances_list.append(instances['InstanceId'])
            response = ec2.stop_instances(InstanceIds=running_instances_list)

        # Disable ng lambda's SQS and CW events
        disable_lambda_triggers()
        disable_cloudwatch_rules()

        StatusCode = 200
        msg = "Process has been completed"

    except Exception as e:
        StatusCode = 500
        log_exception(e)
        msg = "Process has encountered an internal server error."
    return {'statusCode': StatusCode, 'Message': json.dumps(msg)}


def log_exception(e):
    logger.error("Exception: {}".format(e), exc_info=sys.exc_info())

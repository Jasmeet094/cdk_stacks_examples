import boto3
import json
import logging
import os
import sys
logger = logging.getLogger()
logger.setLevel(logging.INFO)


def enable_lambda_triggers():
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
            # Enable triggers based on the event source mappings
            event_source_mappings = client.list_event_source_mappings(
                FunctionName=lambda_name)['EventSourceMappings']
            for mapping in event_source_mappings:
                mapping_id = mapping['UUID']
                client.update_event_source_mapping(
                    UUID=mapping_id, Enabled=True)

            print(f"Triggers enabled for Lambda function: {lambda_name}")

        except client.exceptions.ResourceNotFoundException:
            print(f"Lambda function not found: {lambda_name}")
        except Exception as e:
            print(f"Error enabling triggers for {lambda_name}: {str(e)}")


def enable_cloudwatch_rules():
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
            # Enable CloudWatch rule
            client.enable_rule(Name=rule_name)

            print(f"CloudWatch rule enabled: {rule_name}")

        except client.exceptions.ResourceNotFoundException:
            print(f"CloudWatch rule not found: {rule_name}")
        except Exception as e:
            print(f"Error enabling CloudWatch rule {rule_name}: {str(e)}")


def lambda_handler(event, context):
    try:
        # Resume the ECS Services
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
                        MinCapacity=1,
                        MaxCapacity=10
                    )
                if "nextToken" in response:
                    response = client_ecs.list_services(
                        cluster=clusterArn,
                        nextToken=response['nextToken']
                    )
                else:
                    ConditionString = False

        # Resume RDS Cluster
        client_rds = boto3.client('rds')
        rds_clusters = os.environ['rds_cluster_identifier']\
            .strip("[]").replace(" ", "").replace("'", "")

        if rds_clusters:
            rdsclusterlist = list(rds_clusters.split(","))
            for cluster in rdsclusterlist:
                client_rds.start_db_cluster(
                    DBClusterIdentifier=cluster
                )

        # Resume Docdb Cluster
        client_docdb = boto3.client('docdb')
        docdb_cluster_identifier = os.environ['docdb_cluster_identifier']

        if docdb_cluster_identifier:
            client_docdb.start_db_cluster(
                DBClusterIdentifier=os.environ['docdb_cluster_identifier']
            )

        # Resume EC2 Instances
        stopped_instances_list = []
        ec2 = boto3.client('ec2')

        # Define the names of the instances to resume
        instance_names = ['ssh_tunnel_instance',
                          'ng_ssh_tunnel_instance',
                          'fx-ng-dotnet-console-app']

        # Find instances by name and their stopped state
        ec2_response = ec2.describe_instances(
            Filters=[
                {'Name': 'tag:Name', 'Values': instance_names},
                {'Name': 'instance-state-name', 'Values': ['stopped']}
            ]
        )

        if ec2_response['Reservations']:
            for reservations in ec2_response['Reservations']:
                for instance in reservations['Instances']:
                    stopped_instances_list.append(instance['InstanceId'])

        if stopped_instances_list:
            response = ec2.start_instances(InstanceIds=stopped_instances_list)
            print("Started instances: ", stopped_instances_list)

        # Enbale ng lambda's SQS and CW events
        enable_lambda_triggers()
        enable_cloudwatch_rules()

        StatusCode = 200
        msg = "Process has been completed"

    except Exception as e:
        StatusCode = 500
        log_exception(e)
        msg = "Process has encountered an internal server error."
    return {'statusCode': StatusCode, 'Message': json.dumps(msg)}


def log_exception(e):
    logger.error("Exception: {}".format(e), exc_info=sys.exc_info())

import boto3
import os

sts_client = boto3.client('sts')
assumed_role_object = sts_client.assume_role(
    RoleArn=os.getenv('CROSS_ACCOUNT_ROLE'),
    RoleSessionName="stacks"
)
credentials = assumed_role_object['Credentials']
r53_client = boto3.client(
    'route53',
    aws_access_key_id=credentials['AccessKeyId'],
    aws_secret_access_key=credentials['SecretAccessKey'],
    aws_session_token=credentials['SessionToken'])


def record_set(ResourceProperties, action):
    if ResourceProperties["WEIGHT"] == "-1":
        print("regular record")
        record_set_regular(ResourceProperties, action)
    else:
        print("weighted record")
        record_set_weighted(ResourceProperties, action)


def record_set_regular(ResourceProperties, action):
    r53_client.change_resource_record_sets(
        HostedZoneId=ResourceProperties["HOSTED_ZONE"],
        ChangeBatch={
            "Comment": action,
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": ResourceProperties["RECORD_NAME"],
                        "Type": ResourceProperties["RECORD_TYPE"],
                        "AliasTarget": {
                            "HostedZoneId": ResourceProperties["TARGET_ZONE"],
                            "DNSName": ResourceProperties["TARGET"],
                            "EvaluateTargetHealth": False
                        }
                    }
                },
            ]
        }
    )


def record_set_weighted(ResourceProperties, action):
    r53_client.change_resource_record_sets(
        HostedZoneId=ResourceProperties["HOSTED_ZONE"],
        ChangeBatch={
            "Comment": action,
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": ResourceProperties["RECORD_NAME"],
                        "Type": ResourceProperties["RECORD_TYPE"],
                        'SetIdentifier': ResourceProperties["SET_IDENTIFIER"],
                        'Weight': int(ResourceProperties["WEIGHT"]),
                        "AliasTarget": {
                            "HostedZoneId": ResourceProperties["TARGET_ZONE"],
                            "DNSName": ResourceProperties["TARGET"],
                            "EvaluateTargetHealth": False
                        }
                    }
                },
            ]
        }
    )


def on_create(event):
    print('got create')
    record_set(event["ResourceProperties"], "CREATE")


def on_update(event):
    print('got update')
    try:
        record_set(event["OldResourceProperties"], "DELETE")
    except Exception:
        print("Error deleting, attempting to create...")
    record_set(event["ResourceProperties"], "CREATE")


def on_delete(event):
    print('got delete')
    record_set(event["ResourceProperties"], "DELETE")


def handler(event, context):
    print(event)
    request_type = event['RequestType']
    if request_type == 'Create':
        return on_create(event)
    if request_type == 'Update':
        return on_update(event)
    if request_type == 'Delete':
        return on_delete(event)

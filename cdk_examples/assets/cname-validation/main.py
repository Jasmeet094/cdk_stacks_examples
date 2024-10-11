import boto3
import os
import time

sts_client = boto3.client('sts')
acm_client = boto3.client('acm')

record_name = None
record_value = None


def get_certificate(ResourceProperties):
    # Waits for certificate to be created
    time.sleep(10)
    response = acm_client.list_certificates(
    )
    for i in response['CertificateSummaryList']:
        tags = acm_client.list_tags_for_certificate(
            CertificateArn=i['CertificateArn']
        )
        for k in tags['Tags']:
            if 'wildcard' in k['Value']:
                k['Value'] = k['Value'].replace('wildcard', '*')

            if (k['Value']) == ResourceProperties["TAG"]:
                arn = acm_client.describe_certificate(
                    CertificateArn=i['CertificateArn']
                )
                global record_name
                global record_value
                record_name = (
                    arn['Certificate']
                    ['DomainValidationOptions']
                    [0]['ResourceRecord']['Name'])
                print(record_name)
                record_value = (
                    arn['Certificate']
                    ['DomainValidationOptions']
                    [0]['ResourceRecord']['Value'])
                print(record_value)


def record_set(ResourceProperties, action):
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
    r53_client.change_resource_record_sets(
        HostedZoneId=ResourceProperties["HOSTED_ZONE"],
        ChangeBatch={
            "Comment": action,
            "Changes": [
                {
                    "Action": action,
                    "ResourceRecordSet": {
                        "Name": record_name,
                        "Type": ResourceProperties["RECORD_TYPE"],
                        'TTL': 123,
                        "ResourceRecords": [{
                            'Value': record_value
                        },
                        ]
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
    get_certificate(event["ResourceProperties"])
    request_type = event['RequestType']
    if request_type == 'Create':
        return on_create(event)
    if request_type == 'Update':
        return on_update(event)
    if request_type == 'Delete':
        return on_delete(event)

from aws_cdk import (
    aws_iam as iam,
    aws_s3 as s3,
)
from aws_cdk.aws_s3 import * # noqa


def get_normalized_bucket_name(stack, name):
    """ all buckets should start with stack name and end with account # """
    if not name.startswith(stack.stack_name) and not stack.nested:
        name = f'{stack.stack_name}-{name}'
    if not name.endswith(stack.account):
        name = f'{name}-{stack.account}'
    return name


class Bucket(s3.Bucket):
    """
    When this base class is used to create bucket in one of the stacks,
    and enable encryption,
    add an encryption kwarg with it separately as:
    "s3.BucketEncryption.S3_MANAGED"
    """
    def __init__(self, scope, id, normalize_bucket_name=True, *args, **kwargs):
        if normalize_bucket_name:
            bucket_name = get_normalized_bucket_name(scope, id)
        else:
            bucket_name = None
        super().__init__(scope, id, bucket_name=bucket_name, *args, **kwargs)


class SecureBucket(Bucket):

    def __init__(self, scope, id, *args, **kwargs):
        kwargs['encryption'] = s3.BucketEncryption.KMS_MANAGED
        kwargs['block_public_access'] = s3.BlockPublicAccess(
            restrict_public_buckets=True
        )
        kwargs['versioned'] = True
        super().__init__(scope, id, *args, **kwargs)


class ServiceBucket(Bucket):
    """ creates a bucket for use by a specific service """

    def __init__(self, scope, user, name='service-bucket', *args, **kwargs):
        """
        :param scope: calling stack instance
        :param user: iam user that will have full access to this bucket
        :param name: optional - name of bucket
        """
        kwargs['encryption'] = s3.BucketEncryption.S3_MANAGED
        super().__init__(scope, id=name, *args, **kwargs)
        self.add_to_resource_policy(
            iam.PolicyStatement(
                actions=['*'],
                principals=[user],
                resources=[f'{self.bucket_arn}/*'],
            )
        )


class StaticFilesBucket(ServiceBucket):

    def __init__(
            self,
            scope,  # stack instance
            user,  # iam user that can manage bucket contents
            allowed_origins,  # cors domains
            name='static-files-bucket',
            *args, **kwargs):
        kwargs['encryption'] = s3.BucketEncryption.S3_MANAGED
        super().__init__(scope, user, name, *args, **kwargs)

        self.add_to_resource_policy(
            iam.PolicyStatement(
                actions=['s3:GetObject'],
                principals=[iam.AnyPrincipal()],
                resources=[f'{self.bucket_arn}/*'],
            )
        )
        if allowed_origins:
            self.add_cors_rule(
                allowed_methods=[HttpMethods.GET], # noqa
                allowed_origins=allowed_origins,
                allowed_headers=['Authorization']
            )


class ConfigBucket(Bucket):
    """ creates a bucket for AWS Config """

    def __init__(self, scope, name='config-bucket', *args, **kwargs):
        kwargs['encryption'] = s3.BucketEncryption.S3_MANAGED
        super().__init__(scope, id=name, *args, **kwargs)
        self.add_to_resource_policy(
            iam.PolicyStatement(
                effect=iam.Effect('ALLOW'),
                actions=['s3:GetBucketAcl', 's3:PutObject'],
                principals=[iam.ServicePrincipal("config.amazonaws.com")],
                resources=[
                    f'{self.bucket_arn}',
                    f'{self.bucket_arn}/AWSLogs/'+scope.account+'/*'
                ]
            )
        )


# Simple S3 bucket use for general purpose
class S3Bucket:
    def __init__(self, scope, bucket_name, environment, *args, **kwargs):

        s3.Bucket(
            scope,
            id=bucket_name,
            bucket_name=bucket_name+"-"+environment,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED
        )


# S3 bucket for s3 static website hosting
class StaticWebsiteHosting:
    def __init__(self, scope, bucket_name, host_name, *args, **kwargs):

        s3.Bucket(
            scope,
            id=bucket_name,
            bucket_name=bucket_name,
            block_public_access=s3.BlockPublicAccess.BLOCK_ALL,
            encryption=s3.BucketEncryption.S3_MANAGED,
            website_redirect=s3.RedirectTarget(
                host_name=host_name,
                protocol=s3.RedirectProtocol.HTTPS
            )
        )

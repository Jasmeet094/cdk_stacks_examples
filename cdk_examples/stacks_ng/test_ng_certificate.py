from .modules.certificate import Certificate
from .base.route53 import (
    CNameRecordVerificationFunction,
    CNameRecordVerification
)
from constructs import Construct
from aws_cdk import (
    Stack as stack
)


class Stack(stack):

    def __init__(
            self,
            scope: Construct,
            construct_id: str,
            metadata: dict,
            environment="default",
            **kwargs) -> None:
        super().__init__(
            scope, construct_id, **kwargs)

        cname_verify_function = CNameRecordVerificationFunction(
            self,
            id='cnameVerifyFunction' + construct_id,
            timeout=900,  # time out 900 sec
            metadata=metadata
        )

        certificates = []

        domains = metadata.get('test_domains')
        for domain in domains:
            certificate_arn = self.create_certificate(
                domain,
                environment,
                cname_verify_function.provider,
                metadata)
            certificates.append(certificate_arn)

    def create_certificate(self, domain, environment, provider, metadata):
        certificate = Certificate(
            self,
            "certificate-" + domain + environment,
            environment,
            domain
        )

        CNameRecordVerification(
            self,
            "Cname" + domain,
            domain,
            provider=provider,
            hosted_zone=metadata.get("hostedZoneId")
        )

        return certificate.certificate.certificate_arn

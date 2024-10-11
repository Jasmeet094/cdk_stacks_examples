from aws_cdk import (
    aws_certificatemanager as certificatemanager
)
from aws_cdk import (
    Tags,
    CfnOutput
)


class Certificate:

    def __init__(
            self,
            scope,
            id,
            environment,
            domain_name,
            **kwargs):

        self.certificate = certificatemanager.Certificate(
            scope,
            id+"-"+"certificate"+"-"+environment,
            domain_name=domain_name,
            validation=certificatemanager
            .CertificateValidation.from_dns(kwargs.get("hostedZone"))
        )
        Tags.of(self.certificate).remove("Name")
        Tags.of(self.certificate).add("TAG", str(
            domain_name.replace('*', 'wildcard')))

        CfnOutput(
            scope,
            id="test-"+id,
            value=self.certificate.certificate_arn,
            export_name=str(id.replace('.', '-').replace('*', 'wildcard'))
        )

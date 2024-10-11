from aws_cdk import (
    aws_route53 as route53,
)


class CnameRecord(route53.CnameRecord):

    def __init__(self, scope, record_name, value, zone, ttl, comment=None,
                 *args, **kwargs):
        super().__init__(scope,
                         id='cname' + record_name,
                         record_name=record_name,
                         domain_name=value,
                         zone=zone,
                         ttl=ttl
                         )


class ARecord(route53.ARecord):
    def __init__(self, scope, record_name, values, zone, ttl, comment=None,
                 *args, **kwargs):
        record_target = route53.RecordTarget(values=values)

        super().__init__(scope,
                         id='arecord' + record_name,
                         record_name=record_name,
                         target=record_target,
                         zone=zone,
                         ttl=ttl
                         )


class TextRecord(route53.TxtRecord):
    def __init__(self, scope, record_name, values, zone, ttl, comment=None,
                 *args, **kwargs):
        super().__init__(scope,
                         id='textrecord' + record_name,
                         record_name=record_name,
                         values=values,
                         zone=zone,
                         ttl=ttl
                         )


class MxRecord(route53.MxRecord):
    def __init__(self, scope, record_name, values, zone, ttl, comment=None,
                 *args, **kwargs):
        super().__init__(scope,
                         id='mxrecord' + record_name,
                         record_name=record_name,
                         values=values,
                         zone=zone,
                         ttl=ttl
                         )


class NsRecord(route53.NsRecord):
    def __init__(self, scope, record_name, values, zone, ttl, comment=None,
                 *args, **kwargs):
        super().__init__(scope,
                         id='nsrecord' + record_name,
                         record_name=record_name,
                         values=values,
                         zone=zone,
                         ttl=ttl
                         )

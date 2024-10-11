from aws_cdk import (
    aws_route53 as route53
)
from .base import dns
from constructs import Construct
from aws_cdk import Stack as stack, Duration


class Stack(stack):

    def __init__(self, scope: Construct, id: str,
                 metadata: dict, environment="default", **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        zone_id = metadata.get('hostedZoneId')
        zone_name = metadata.get('hostedZone')
        zone = route53.HostedZone.from_hosted_zone_attributes(
            self,
            'id' + zone_name,
            hosted_zone_id=zone_id,
            zone_name=zone_name)

        # Cname records for GUide CX
        dns.CnameRecord(self,
                        record_name="em4543",
                        value="u6664149.wl150.sendgrid.net",
                        zone=zone,
                        ttl=Duration.seconds(3600)
                        )

        # A record for Ips
        dns.ARecord(self,
                    record_name="",
                    values=['75.2.70.75', '99.83.190.102'],
                    zone=zone,
                    ttl=Duration.seconds(300)
                    )

        # MX record for mail server
        mx_record_value = route53.MxRecordValue(
            host_name='test-com.mail.protection.outlook.com.',
            priority=0)

        dns.MxRecord(self,
                     record_name="",
                     values=[mx_record_value],
                     zone=zone,
                     ttl=Duration.seconds(3600)
                     )

        # Text records
        dns.TextRecord(
            self,
            record_name="",
            values=[
                "google-site-verification=GAAksQi_EGDHD_LzCk2hFumer4OQfljHFbRjjhhYgwQ", # noqa
                "v=spf1 include:%{i}._ip.%{h}._ehlo.%{d}._spf.vali.email ~all", # noqa
                "adobe-idp-site-verification=641292268bd52b51844531959435179627c4bef124ff8848210ca73fa862a112",  # noqa
                "ZOOM_verify_kAi_pSAMRzC8u8FgtQABGA",
                "twilio-domain-verification=362bdf541e6470b7872fae8d93383352",  # noqa
                "google-site-verification=s46odeloK2_42SHZynYE5hq5DWyUegoW5yaptskmLF0",  # noqa
                "google-site-verification=59O-K5mlesT-jFCvGGEv5WU2unxYBQ-SE1F3EwAJGUg", # noqa
                "google-site-verification=0hv0WWJIp31u0eYUOTYEUEKyV1dq9yBa5HKVBQA2nko", # noqa
            ],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.TextRecord(
            self,
            record_name="_amazonses",
            values=["nSgVoDEvhpRT1T2du3KLqAHxYPX+VWsQBR2xw/ElWqI="],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.TextRecord(
            self,
            record_name="google._domainkey",
            values=[
                "v=DKIM1; k=rsa; p=MIIBIjANBgkqhkiG9w0BAQEFAAOCAQ8AMIIBCgKCAQEAq552IU+19NGjD47o8/2tD97hDcwgWXisAE8lvPNM5ek4Y8qMB676BioNchA19GcBhwAtc8wt1zZjK7yx3XuQ+kXrWYD/eQlHgIuotNuzt/VYMb0oGW0fMtRsQTphZ0aQEs6doEfXECrY/eJa1Cco5XkIod3NBsLy4nJXPKMWiJeZBhMBrbmTZijP7LH5XF0+s" "WpimWaX1ADg6DOI7MP3zV4uLvkU/7xMsx1XwiBcDHv+fTfuHdkJshkPLdEhDldT6438ddY7bIrCv/EfsITP/5yFtjrqYshBsF5FPyQr6Fb27WUS7AyotOu3wUavVF6n16E+ojlWnpEj7O6gdW4lAwIDAQAB" # noqa
            ],
            zone=zone,
            ttl=Duration.seconds(300)
        )

        # Cname records for validation
        dns.CnameRecord(
            self,
            record_name="_b3707023c0aaa0cd2dc82ad7f270cd40",
            value="_c5c128112c1f310262e8a4df34f925cc.vtqfhvjlcp.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_0161f177428b860091347adcfc670d9e.stage.admin2",
            value="_dce0498504eb99cde5f74ac0f0a2700d.hkmpvcwbzw.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_d91ee6d326f223b1405b7ec082955019.stage.admin",
            value="_1ca25effcc745ef0c1447b79af78c767.hkmpvcwbzw.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_c0a6a87d6aa0c4ed0e34a920d22a35c1.dev.admin",
            value="_ebdabbfde20e8a8e71322935543185cb.jddtvkljgg.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_0804c2ae2c1c0a549c7dd574c06ec059.stage.api-stage",
            value="_62aef5ee00470aa14ad61567499b6356.mvtxpqxpkb.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_e6fb8d76b477015f9ae143f9b73c1dc5.stage.api",
            value="_2d59ff7d785d695cb342c7e0c35596ef.zjfbrrwmzc.acm-validations.aws.",  # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_547e8a78b0b02b07bae71b9bf49a5f4f.dev.api",
            value="_72d09102c4406959948cff9ab77d5a76.jddtvkljgg.acm-validations.aws.",  # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_091454012419924d529681ff32102e29.dev.api-dev",
            value="_b584fd9d3b582cea4b207f6df2c52412.mvtxpqxpkb.acm-validations.aws.",  # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_5b34c7299f00e40664e3fb154e29bd78.dev.test-app",
            value="_74ff3c27f9b6c6a78918547bf65e7cee.vtqfhvjlcp.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_5f915e38ab41b12bf865517ba6f7a2fd.stage.test-app",
            value="_91e87b570cae3008d749907c08367c6b.hkmpvcwbzw.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_1637eb41637208b00a06a8332c583e1d.help",
            value="_8f5b4b7f1257a7f6a2bee5482f9fb9fc.tljzshvwok.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.CnameRecord(
            self,
            record_name="_7f6347a5b12cd7906dafdb4d7acdcf5b.stage.platform",
            value="_e13622e357a61fc57f752d14d7e5670b.nfyddsqlcy.acm-validations.aws", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_c367e287336b6d4d5155ef275f0f0c40.dev.portal.test.com", # noqa
            value="_2db4274e957592c46ba517ad2fb55092.hkmpvcwbzw.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_283439565ec90a9cd2ad32ada9eef03c.stage.portal",
            value="_e5fe8d7295039ef25b4e42e484efc532.hkmpvcwbzw.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_0c05bfcafe1f447c00932049f381214a.dev.app",
            value="_051c49a176c68fd51cb9dd90b7e70a56.qqqfmgwtgn.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_fc934d124e7ee02368d1e23807305f0e.demo.enablear.test.com.", # noqa
            value="_dfdb1b42c9155c7d56a34a2c2b94c511.lggsghvbmf.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="iapk3h4kqcqjg23ejobojvffgo4xx4if._domainkey.test.com",  # noqa
            value="iapk3h4kqcqjg23ejobojvffgo4xx4if.dkim.amazonses.com",  # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="q62blhel2swhavmf2ny4jeiknljmj2uk._domainkey.test.com",  # noqa
            value="q62blhel2swhavmf2ny4jeiknljmj2uk.dkim.amazonses.com",  # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="wsjjo3u45aawxg42mxyyrpuqvddqxhww._domainkey.test.com",  # noqa
            value="wsjjo3u45aawxg42mxyyrpuqvddqxhww.dkim.amazonses.com",  # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        # Ns records for name server
        dns.NsRecord(
            self,
            record_name="_dmarc",
            values=["ns.vali.email."],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.NsRecord(
            self,
            record_name="_domainkey",
            values=["ns.vali.email."],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName record for domainconnect
        dns.CnameRecord(
            self,
            record_name="_domainconnect",
            value="connect.domains.google.com.",
            zone=zone,
            ttl=Duration.seconds(21600)
        )

        dns.CnameRecord(
            self,
            record_name="api-demo6",
            value="spherical-sheep-os6l0wwynxil0ncojiyep7bq.herokudns.com",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName records for api
        dns.CnameRecord(
            self,
            record_name="api-shield",
            value="pacific-shore-4735.desolate-cove-9676.herokuspace.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.CnameRecord(
            self,
            record_name="api1",
            value="apiprod-1408986399.us-west-2.elb.amazonaws.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.CnameRecord(
            self,
            record_name="api-prod",
            value="vast-pomelo-65tq871f9xde9xyal088xfwn.herokudns.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.CnameRecord(
            self,
            record_name="api-stage",
            value="fast-acai-s2pwuyaqjajlx4y4yhw4ew8f.herokudns.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for auto discover
        dns.CnameRecord(
            self,
            record_name="autodiscover",
            value="autodiscover.outlook.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        ##
        # CName Record for blog
        dns.CnameRecord(
            self,
            record_name="blog",
            value="8432121.group21.sites.hubspot.net.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for client
        dns.CnameRecord(
            self,
            record_name="client",
            value="elliptical-beach-7qjvd5obzn8qoaecks7c4f4v.herokudns.com.", # noqa
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # A Record for dev
        dns.ARecord(
            self,
            record_name="dev",
            values=['64.71.72.136'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for em4310
        dns.CnameRecord(
            self,
            record_name="em4310",
            value="u8297650.wl151.sendgrid.net.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for enterpriseenrollment
        dns.CnameRecord(
            self,
            record_name="enterpriseenrollment",
            value="enterpriseenrollment.manage.microsoft.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for enterpriseregistration
        dns.CnameRecord(
            self,
            record_name="enterpriseregistration",
            value="enterpriseregistration.windows.net.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # A Record for go
        dns.ARecord(
            self,
            record_name="go",
            values=['52.72.13.96'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for googlebb21292650146555
        dns.CnameRecord(
            self,
            record_name="googlebb21292650146555",
            value="google.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for googleddee6e2dc44e4635
        dns.CnameRecord(
            self,
            record_name="googleddee6e2dc44e4635",
            value="google.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for custom.intercom.help
        dns.CnameRecord(
            self,
            record_name="custom.intercom.help",
            value="_8f5b4b7f1257a7f6a2bee5482f9fb9fc.tljzshvwok.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for wbt7kvvagz2o.help
        dns.CnameRecord(
            self,
            record_name="wbt7kvvagz2o.help",
            value="gv-tbcbhazm4iqfyg.dv.googlehosted.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for info
        dns.CnameRecord(
            self,
            record_name="info",
            value="8432121.group21.sites.hubspot.net.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for lyncdiscover
        dns.CnameRecord(
            self,
            record_name="lyncdiscover",
            value="webdir.online.lync.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for multidomaindemo2
        dns.CnameRecord(
            self,
            record_name="multidomaindemo2",
            value="larval-longan-lc2qyfkpla0sltsv2vqi3ezq.herokudns.com",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for payments
        dns.CnameRecord(
            self,
            record_name="payments",
            value="www195.wixdns.net.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for www.payments
        dns.CnameRecord(
            self,
            record_name="www.payments",
            value="www195.wixdns.net.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for portal
        dns.CnameRecord(
            self,
            record_name="portal",
            value="aerodynamic-hare-km12l1gb7gh7vf1laueqcls2.herokudns.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for proddb
        dns.CnameRecord(
            self,
            record_name="proddb",
            value="prodonenetworks.c7vlidbn8rwd.us-west-2.rds.amazonaws.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for qa
        dns.CnameRecord(
            self,
            record_name="qa",
            value="portalqa-457665422.us-west-2.elb.amazonaws.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # A Record for production
        dns.ARecord(
            self,
            record_name="production",
            values=['35.161.95.30'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # A Record for o1.ptr8546
        dns.ARecord(
            self,
            record_name="o1.ptr8546",
            values=['149.72.170.233'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for sftp
        dns.CnameRecord(
            self,
            record_name="sftp",
            value="ec2-35-166-152-30.us-west-2.compute.amazonaws.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for sip
        dns.CnameRecord(
            self,
            record_name="sip",
            value="sipdir.online.lync.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # A Record for staging
        dns.ARecord(
            self,
            record_name="staging",
            values=['35.161.131.51'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for subdomain
        dns.CnameRecord(
            self,
            record_name="subdomain",
            value="api.test.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for vault
        dns.CnameRecord(
            self,
            record_name="vault",
            value="ec2-54-213-252-99.us-west-2.compute.amazonaws.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for stage.workflow
        dns.CnameRecord(
            self,
            record_name="stage.workflow",
            value="finex-nlbfi-uw5kfoiyditk-0bf7cb080f51f862.elb.us-east-1.amazonaws.com.", # noqa
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for www
        dns.CnameRecord(
            self,
            record_name="www",
            value="proxy-ssl.webflow.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for zendesk1
        dns.CnameRecord(
            self,
            record_name="zendesk1",
            value="mail1.zendesk.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for zendesk2
        dns.CnameRecord(
            self,
            record_name="zendesk2",
            value="mail2.zendesk.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for zendesk3
        dns.CnameRecord(
            self,
            record_name="zendesk3",
            value="mail3.zendesk.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName Record for zendesk4
        dns.CnameRecord(
            self,
            record_name="zendesk4",
            value="mail4.zendesk.com.",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # Text Record for zendeskverification
        dns.TextRecord(
            self,
            record_name="zendeskverification",
            values=["c7eb975fc4420e64"],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # A Record for SSH Tunnel
        dns.ARecord(
            self,
            record_name="dev.sshtunnel",
            values=['54.173.47.243'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.ARecord(
            self,
            record_name="stage.sshtunnel",
            values=['3.234.195.47'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.ARecord(
            self,
            record_name="prod.sshtunnel",
            values=['44.193.238.89'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.ARecord(
            self,
            record_name="dev-ng-ssh-tunnel",
            values=['18.208.7.125'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.ARecord(
            self,
            record_name="stage-ng-ssh-tunnel",
            values=['52.23.115.57'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        dns.ARecord(
            self,
            record_name="qa-ng-ssh-tunnel",
            values=['34.236.64.71'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName record for salesloft
        dns.CnameRecord(
            self,
            record_name="loft",
            value="custom-tracking.salesloft.com",
            zone=zone,
            ttl=Duration.seconds(3600)
        )
        # Arecord for ssh tunnel dev
        dns.ARecord(
            self,
            record_name="dev-ssh-tunnel",
            values=['3.230.227.174'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # Arecord for ssh tunnel qa
        dns.ARecord(
            self,
            record_name="qa-ssh-tunnel",
            values=['44.216.244.156'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # Arecord for ssh tunnel stage
        dns.ARecord(
            self,
            record_name="stage-ssh-tunnel",
            values=['52.1.224.250'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # Arecord for ssh tunnel production
        dns.ARecord(
            self,
            record_name="prod-ssh-tunnel",
            values=['52.5.2.111'],
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName record for learn
        dns.CnameRecord(
            self,
            record_name="learn",
            value="4e24a74a32f946d9b03ab0cf184451d7.unbouncepages.com",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        # CName records for CloudFront
        dns.CnameRecord(
            self,
            record_name="dev-cdn-admin-static",
            value="d3ey5c8ois250l.cloudfront.net",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="dev-cdn-platform-static",
            value="d1ucqerv3kf3yq.cloudfront.net",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="cdn-admin-static",
            value="d10nh4aw9qddv8.cloudfront.net",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="cdn-platform-static",
            value="d3dbuu39g34t3f.cloudfront.net",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="stage-cdn-admin-static",
            value="d26wiy2ct1rvu3.cloudfront.net",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="stage-cdn-platform-static",
            value="d1ugr387j0gpv6.cloudfront.net",
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_8b464ec301fd06fd9173dca8965bfef9.dev.portal2",
            value="_5436126e5f225e048b8fec4ea84ac03a.dlgthlwgnp.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        dns.CnameRecord(
            self,
            record_name="_977bcbbdfd85578e678a4785f2bd483c.stage.portal2",
            value="_e50d4467dd681656db1b463d1bbf7456.dlgthlwgnp.acm-validations.aws.", # noqa
            zone=zone,
            ttl=Duration.seconds(300)
        )

        # Cname records for outgrow
        dns.CnameRecord(self,
                        record_name="calculator",
                        value="cname-ssl.outgrow.co",
                        zone=zone,
                        ttl=Duration.seconds(3600)
                        )

        # Cname records for DocumentDBs

        dns.CnameRecord(self,
                        record_name="dev.mongo",
                        value="documentdb-5-test-ng-test-dev.cluster-cfebvheveqxn.us-east-1.docdb.amazonaws.com", # noqa
                        zone=zone,
                        ttl=Duration.seconds(3600)
                        )

        dns.CnameRecord(self,
                        record_name="stage.mongo",
                        value="documentdb-test-ng-test-stage.cluster-crqrriv7genk.us-east-1.docdb.amazonaws.com", # noqa
                        # noqa
                        zone=zone,
                        ttl=Duration.seconds(3600)
                        )

        dns.CnameRecord(self,
                        record_name="qa.mongo",
                        value="documentdb-test-ng-test-qa-new.cluster-cdvspc8qqrol.us-east-1.docdb.amazonaws.com", # noqa
                        # noqa
                        zone=zone,
                        ttl=Duration.seconds(3600)
                        )

        # CName records for zendesk support
        dns.CnameRecord(
            self,
            record_name="support",
            value="test.zendesk.com",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # CName records for mendix
        dns.CnameRecord(
            self,
            record_name="nextvue",
            value="test-portal.mendixcloud.com",
            zone=zone,
            ttl=Duration.seconds(3600)
        )

        # NS record for BIMI
        dns.NsRecord(
            self,
            record_name="_bimi",
            values=["ns.vali.email."],
            zone=zone,
            ttl=Duration.seconds(300)
        )

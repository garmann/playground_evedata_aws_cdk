import requests, socket

from aws_cdk import (
    aws_ec2 as ec2,
    aws_elasticsearch as elasticsearch,
    aws_rds as rds,
    core
)


class PlaygroundEvedataAwsCdkStack(core.Stack):

    def __init__(self, scope: core.Construct, id: str, **kwargs) -> None:
        super().__init__(scope, id, **kwargs)

        r = requests.get("http://ifconfig.me")
        myip = r.text + "/32"

        vpc = ec2.Vpc(self, "VPC",
                      nat_gateways=0,
                      max_azs=3,
                      subnet_configuration=
                        [ec2.SubnetConfiguration(name="public", subnet_type=ec2.SubnetType.PUBLIC)]
                      )

        amzn_linux = ec2.MachineImage.latest_amazon_linux(
            generation=ec2.AmazonLinuxGeneration.AMAZON_LINUX_2,
            edition=ec2.AmazonLinuxEdition.STANDARD,
            virtualization=ec2.AmazonLinuxVirt.HVM,
            storage=ec2.AmazonLinuxStorage.GENERAL_PURPOSE
        )

        sg = ec2.SecurityGroup(self, "greg-sg", vpc=vpc, allow_all_outbound=True)
        # sg.add_ingress_rule(ec2.Peer.ipv4(myip), ec2.Port.tcp(22))

        instance = ec2.Instance(self, "greg-ec2",
                                    instance_type=ec2.InstanceType('c5.xlarge'),
                                    machine_image=amzn_linux,
                                    vpc=vpc,
                                    key_name='gregkey', security_group=sg)


        core.CfnOutput(self, "output_ssh_bastion_public_ip",
                       value=instance.instance_public_ip)
        core.CfnOutput(self, "output_ssh_bastion_private_ip",
                       value=instance.instance_private_ip)

        # es domain helpful links
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchclusterconfig
        # https://github.com/aws/aws-cdk/issues/2873
        # https://sourcecodequery.com/example-method/core.Tag
        # https://docs.aws.amazon.com/AWSCloudFormation/latest/UserGuide/aws-resource-elasticsearch-domain.html#cfn-elasticsearch-domain-elasticsearchclusterconfig

        es_cluster_config = {
            "InstanceCount": 3,
            "InstanceType": "m4.xlarge.elasticsearch",
            "DedicatedMasterEnabled": True,
            "DedicatedMasterCount": 3
        }
        es_access_policy = {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Effect": "Allow",
                    "Principal": {
                        "AWS": "*"
                    },
                    "Action": [
                        "es:*"
                    ],
                    "Condition": {
                        "IpAddress": {
                            "aws:SourceIp": [
                                myip, instance.instance_public_ip, instance.instance_private_ip
                            ]
                        }
                    },

                }
            ]
        }
        es_storage = {
                "ebsEnabled": True,
                "volumeSize": 50,
                "volumeType": "gp2"
        }

        es_domain = elasticsearch.CfnDomain(self, "greg-es", elasticsearch_version="7.4",
                                                elasticsearch_cluster_config=es_cluster_config,
                                                access_policies=es_access_policy,
                                                ebs_options=es_storage,
                                                )

        core.CfnOutput(self, "output_es_domain_endpoint",
                       value=es_domain.attr_domain_endpoint)


        # play with vpc attr import
        # https://docs.aws.amazon.com/cdk/api/latest/python/aws_cdk.aws_ec2/Vpc.html
        # - from_lookup
        # - from_vpc_attributes
        # lookup_vpc = ec2.Vpc.from_lookup(self, "defaultstuff", vpc_id="vpc-964376fd")
        # print(lookup_vpc.vpc_cidr_block)

        # db_sg = rds.CfnDBSecurityGroup(self, 'greg-dbsg',
        #                                ec2_vpc_id=vpc,
        #                                group_description="gregs-sec-group",
        #                                db_security_group_ingress=)
        #
        # db_sg_ingress = rds.CfnDBSecurityGroupIngress(self, 'greg-dbsg-ingress',
        #                                                 cidrip="10.0.0.0/8",
        #                                                 db_security_group_name="greg-dbsg"
        # )
        #
        # # https://github.com/aws-samples/aws-cdk-examples/blob/master/python/rds/app.py
        # db = rds.DatabaseInstance(
        #     self, "RDS",
        #     master_username="XXakjsfhajdshflkadshfk",
        #     master_user_password=core.SecretValue.plain_text("XXakjsfhajdshasdasdakjsd"),
        #     database_name="evedata",
        #     engine_version="8.0.16",
        #     engine=rds.DatabaseInstanceEngine.MYSQL,
        #     vpc=vpc,
        #     port=3306,
        #     instance_type=ec2.InstanceType.of(
        #         ec2.InstanceClass.MEMORY4,
        #         ec2.InstanceSize.LARGE,
        #     ),
        #     removal_policy=core.RemovalPolicy.DESTROY,
        #     deletion_protection=False,
        #     #security_groups=db_sg
        # )

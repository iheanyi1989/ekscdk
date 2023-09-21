from aws_cdk import (
    Stack,
    aws_eks as eks,
    aws_ecr as ecr,
    aws_iam as iam,
    aws_ec2 as ec2,
    RemovalPolicy
)
from constructs import Construct

class EksStack(Stack):

    def __init__(self, scope: Construct, construct_id: str, **kwargs) -> None:
        super().__init__(scope, construct_id, **kwargs)

        # Create a VPC with default configuration
        vpc = ec2.Vpc(self, 'MyEKSVPC')

        # Creates an ECR Repository
        repo = ecr.Repository(self, 'MyECRRepo',
                              repository_name='dbecrrepo')

        # Creates an IAM role for EKS Cluster
        cluster_role = iam.Role(self, 'ClusterAdminRole',
                                assumed_by=iam.ServicePrincipal('eks.amazonaws.com'),
                                managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSClusterPolicy')]
                                )

        # Create an IAM role for system:masters
        masters_role = iam.Role(self, "MastersRole",
                                assumed_by=iam.ServicePrincipal("sts.amazonaws.com"))
        masters_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSClusterPolicy"))
        masters_role.add_managed_policy(iam.ManagedPolicy.from_aws_managed_policy_name("AmazonEKSWorkerNodePolicy"))

        # Creates an EKS Cluster with masters_role
        cluster = eks.Cluster(self, 'MyCluster',
                              vpc=vpc,
                              default_capacity=0,
                              version=eks.KubernetesVersion.V1_25,
                              role=cluster_role,
                              masters_role=masters_role,  # Associate the masters role
                              cluster_name='dbekscluster'
                              )

        # Creates a linux node group with security configurations
        nodegroup = cluster.add_nodegroup_capacity('MyNodeGroup',
                                                   nodegroup_name='mynodegroup',
                                                   instance_types=[ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO)],
                                                   min_size=2,
                                                   max_size=5,
                                                   desired_size=3,
                                                   subnets=ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
                                                   )

        # Define a VPC Endpoint for S3 (as an example)
        s3_endpoint = vpc.add_gateway_endpoint('S3Endpoint',
                                               service=ec2.GatewayVpcEndpointAwsService.S3,
                                               subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)]
                                               )

        # Apply Removal Policy
        resources = [vpc, nodegroup, repo, cluster_role, s3_endpoint]
        for resource in resources:
            resource.apply_removal_policy(RemovalPolicy.DESTROY)

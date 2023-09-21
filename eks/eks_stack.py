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

        # The code that defines your stack goes here
        # Create a VPC with default configuration
        vpc = ec2.Vpc(self, 'MyEKSVPC'
                      )
        
        
        # Creates an ECR Repository
        repo = ecr.Repository(self, 'MyECRRepo',
                              repository_name = 'dbecrrepo')
        
        
        # Creates an IAM role for EKS Cluster
        cluster_role = iam.Role(self, 'ClusterAdminRole',
                                assumed_by=iam.ServicePrincipal('eks.amazonaws.com'),
                                managed_policies=[iam.ManagedPolicy.from_aws_managed_policy_name('AmazonEKSClusterPolicy')]
                            )
        
        # Creates an EKS Cluster
        cluster = eks.Cluster(self, 'MyCluster',
                              vpc=vpc,
                              default_capacity=0,
                              version=eks.KubernetesVersion.V1_25,
                              role=cluster_role,
                              cluster_name='dbekscluster'
                              )
        
        # Cretaes a linux node group with security configurations
        nodegroup = cluster.add_nodegroup_capacity('MyNodeGroup',
                                                   nodegroup_name= 'mynodegroup',
                                                   instance_types=[ec2.InstanceType.of(ec2.InstanceClass.BURSTABLE3, ec2.InstanceSize.MICRO)], 
                                                   min_size = 2,
                                                   max_size = 5,
                                                   desired_size = 3,
                                                   subnets = ec2.SubnetSelection(subnet_type=ec2.SubnetType.PUBLIC)
                                            )
        
        # # Defines security group for EKS node group
        # node_sg = ec2.SecurityGroup(self, 'NodeSecGroup',
        #                             vpc=vpc,
        #                             allow_all_outbound= True) #Set to false to restrict outbound traffic
        
        # # Allows specific inbound traffic. For eg, allow traffic on port 80:
        # node_sg.add_ingress_rule(ec2.Peer.any_ipv4(), ec2.Port.tcp(80), 'Allow HTTP Traffic')
        
        # # Associate security group with Node group
        # nodegroup.add_
        
        # Define a VPC Endpoint for S3 (as an example)
        s3_endpoint = vpc.add_gateway_endpoint('S3Endpoint',
                                              service=ec2.GatewayVpcEndpointAwsService.S3, 
                                              subnets=[ec2.SubnetSelection(subnet_type=ec2.SubnetType.PRIVATE_WITH_EGRESS)]
                                              )
        # Apply Removal Policy
        resources = [ vpc, nodegroup, repo, cluster_role, s3_endpoint]
        for resource in resources:
                resource.apply_removal_policy(RemovalPolicy.DESTROY)
        
        
        
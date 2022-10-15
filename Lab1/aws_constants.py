import boto3

EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')
ELB_CLIENT = boto3.client('elbv2')
SSM_CLIENT = boto3.client('ssm')
SN_ALL = EC2_CLIENT.describe_subnets()  # Obtain a list of all subnets
N_SUBNETS = len(SN_ALL['Subnets'])  # Obtain amount of subnets
M4_NUM_INSTANCES = 1  # number of M4 instances to create
T2_NUM_INSTANCES = 1  # number of T2 instances to create

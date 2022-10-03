# Sets up a security group. Creates instances, target groups and elastic load balancers.
import time

import boto3
from botocore.exceptions import ClientError

# Global variables
EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')
ELB_CLIENT = boto3.client('elbv2')
SSM_CLIENT = boto3.client('ssm')
SN_ALL = EC2_CLIENT.describe_subnets()  # Obtain a list of all subnets
N_SUBNETS = len(SN_ALL['Subnets'])  # Obtain amount of subnets
USERDATA_SCRIPT = """#!/bin/bash
mkdir flask_application && cd flask_application
pip install Flask

cat << EOF > flask_app.py
#!/usr/bin/python
from flask import Flask
app = Flask(__name__)

@app.route('/')
def my_app():
    return 'Worked!'
EOF

chmod 755 flask_app.py

export flask_application=flask_app.py
flask run
"""


# Function to create {num_instances} amount of {instance_type} instances
# Returns a list of instance objects
def create_ec2(num_instances, instance_type):
    instances = []
    for i in range(num_instances):
        instances.append(EC2_RESOURCE.create_instances(
            ImageId='ami-0149b2da6ceec4bb0',
            # ubuntu 20.04 x86 (free) (the one we used in the first lab session iirc)
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            # we will change accordingly (t2.nano is free for testing purposes)
            SecurityGroupIds=[security_group_id],
            # we use the security group id just created above.
            SubnetId=SN_ALL['Subnets'][i % N_SUBNETS]['SubnetId'],
            # we distribute instances evenly across all subnets
            UserData=USERDATA_SCRIPT,
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': instance_type + '-lab1-ec2-instance-' + str(i + 1)
                        },
                    ]
                },
            ]
        )[0])
        print(f'{instances[i]} is starting')
    return instances


# Function to create a target group called {group_name} that includes {instances}
# Returns the target group's arn
def create_tg(
        group_name,
        vpc_id,
        instances):
    elb_response = ELB_CLIENT.create_target_group(
        Name=group_name,
        Protocol='HTTP',
        Port=80,
        VpcId=vpc_id
    )
    targ_grp_arn = elb_response['TargetGroups'][0]['TargetGroupArn']

    print('Waiting for instance(s) to start running...')
    for instance in instances:
        instance.wait_until_running()
        response = ELB_CLIENT.register_targets(
            TargetGroupArn=targ_grp_arn,
            Targets=[
                {
                    'Id': instance.id
                }
            ]
        )
    return targ_grp_arn


# Function to create a elastic load balancer called {elb_name} and attach it to target group with arn {tg_arn}
# Returns ___
def create_elb(elb_name, tg_arn):
    subnet_ids = []
    for i in range(N_SUBNETS):
        subnet_ids.append(SN_ALL['Subnets'][i]['SubnetId'])

    elb = ELB_CLIENT.create_load_balancer(
        Name=elb_name,
        Subnets=subnet_ids,
        Scheme='internet-facing',
        Type='application',
        IpAddressType='ipv4'
    )

    # Attach ELB to Target Group
    response = ELB_CLIENT.create_listener(
        DefaultActions=[{
            'TargetGroupArn': tg_arn,
            'Type': 'forward',
        }, ],
        LoadBalancerArn=elb['LoadBalancers'][0]['LoadBalancerArn'],
        Port=80,
        Protocol='HTTP',
    )
    return


# get our virtual cloud id
vpc_response = EC2_CLIENT.describe_vpcs()
vpc_id = vpc_response.get('Vpcs', [{}])[0].get('VpcId', '')

print('CREATING SECURITY GROUP')
sec_group_name = 'lab1-security-group'
try:
    response = EC2_CLIENT.create_security_group(
        GroupName=sec_group_name,
        Description='Security group for the ec2 instances used in Lab1',
        VpcId=vpc_id
    )
    security_group_id = response['GroupId']
    # TODO For scripting, we should probably save the security group somewhere 
    # in a file (so that it can be used with bash) ?
    print(f'Successfully created security group {security_group_id}')
    sec_group_rules = [
        {'IpProtocol': 'tcp',
         'FromPort': 22,
         'ToPort': 22,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
         'FromPort': 80,
         'ToPort': 80,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
        {'IpProtocol': 'tcp',
         'FromPort': 443,
         'ToPort': 443,
         'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        # TODO maybe we should add ssh redirection ?
    ]
    data = EC2_CLIENT.authorize_security_group_ingress(GroupId=security_group_id,
                                                       IpPermissions=sec_group_rules)
    print(f'Successfully updated security group rules with : {sec_group_rules}')
except ClientError as e:
    try:  # if security group exists already, find the security group id
        response = EC2_CLIENT.describe_security_groups(
            Filters=[
                dict(Name='group-name', Values=[sec_group_name])
            ])
        security_group_id = response['SecurityGroups'][0]['GroupId']
        print(e)
    except ClientError as e:
        print(e)
        exit(1)

# Create an instances with the created security group rules
print('CREATING INSTANCES ASSOCIATED WITH THE SECURITY GROUP')
m4_num_instances = 3  # number of instances to create
m4_instance_type = 't2.nano'  # change to m4.large
m4_instances = create_ec2(m4_num_instances, m4_instance_type)

# Create a target group for the instances created
print('CREATING A TARGET GROUP FOR THE M4 INSTANCES AND REGISTERING THEM')
m4_group_name = 'm4-Group'
m4_group_arn = create_tg(m4_group_name, vpc_id, m4_instances)

# Create a load balancer for the target group created
print('CREATING LOAD BALANCER AND ATTACHING IT TO M4 TARGET GROUP')
m4_elb_name = 'm4-load-balancer'
create_elb(m4_elb_name, m4_group_arn)

# print('DELETE LOAD BALANCER')
# ELB_CLIENT.delete_load_balancer(LoadBalancerArn=m4_group_arn)
# print('STOPPING INSTANCES')
# EC2_CLIENT.terminate_instances(InstanceIds=[i.id for i in m4_instances])

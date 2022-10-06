# Sets up a security group. Creates instances, target groups and elastic load balancers.
import boto3
from botocore.exceptions import ClientError

# Global variables
EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')
ELB_CLIENT = boto3.client('elbv2')
SSM_CLIENT = boto3.client('ssm')
SN_ALL = EC2_CLIENT.describe_subnets()  # Obtain a list of all subnets
N_SUBNETS = len(SN_ALL['Subnets'])  # Obtain amount of subnets
M4_NUM_INSTANCES = 1            #number of M4 instances to create 
T2_NUM_INSTANCES = 1            #number of T2 instances to create
# create key pair (probably not necessary)
# key_name = 'vockey'
# try:
#     KEY_PAIR = EC2_CLIENT.create_key_pair(KeyName=key_name)
# except ClientError:
#     KEY_PAIR= key_name

USERDATA_SCRIPT = """#!/bin/bash
apt update && \
    apt install -y python3 python3-flask pip && \
    mkdir /root/flask_application

pip install ec2_metadata

cat << EOF > /root/flask_application/my_app.py
#!/usr/bin/python
from flask import Flask
from ec2_metadata import ec2_metadata
app = Flask(__name__)

@app.route('/')
def my_app():
    return 'Instance id-' + ec2_metadata.instance_id + ' is telling you to use /cluster1 or /cluster2'

@app.route('/cluster1')
def my_app1():
    return 'Instance id-' + ec2_metadata.instance_id + ' is responding now!'

@app.route('/cluster2')
def my_app2():
    return 'Instance id-' + ec2_metadata.instance_id + ' is responding now!'
EOF

chmod 755 my_app.py
export FLASK_APP=/root/flask_application/my_app.py
flask run --host 0.0.0.0 --port 80
"""


# Function to create {num_instances} amount of {instance_type} instances
# Returns a list of instance objects
def create_ec2(num_instances, instance_type, sg_id):
    instances = []
    for i in range(num_instances):
        instances.append(EC2_RESOURCE.create_instances(
            ImageId='ami-0149b2da6ceec4bb0',
            # ubuntu 20.04 x86 (free) (the one we used in the first lab session iirc)
            MinCount=1,
            MaxCount=1,
            InstanceType=instance_type,
            Monitoring={'Enabled':True},
            # KeyName=KEY_PAIR,
            # we will change accordingly (t2.nano is free for testing purposes)
            SecurityGroupIds=[sg_id],
            # we use the security group id just created above.
            SubnetId=SN_ALL['Subnets'][i % N_SUBNETS]['SubnetId'],
            # we distribute instances evenly across all subnets
            UserData=USERDATA_SCRIPT.replace('INSTANCE_ID_PLACEHOLDER', str(i + 1)),
            TagSpecifications=[
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Name',
                            'Value': 'lab1-ec2-instance-' + str(i + 1)
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
def create_elb(elb_name, tg1_arn, tg2_arn, sg_id):
    subnet_ids = []
    for i in range(N_SUBNETS):
        subnet_ids.append(SN_ALL['Subnets'][i]['SubnetId'])

    elb = ELB_CLIENT.create_load_balancer(
        Name=elb_name,
        Subnets=subnet_ids,
        Scheme='internet-facing',
        Type='application',
        SecurityGroups=[sg_id],
        IpAddressType='ipv4'
    )

    # Attach ELB to Target Group
    listener = ELB_CLIENT.create_listener(
        DefaultActions=[{
            'Type': 'fixed-response',
            'FixedResponseConfig': {
                    'MessageBody': 'Please use /cluster1 or /cluster2',
                    'StatusCode': '503',
                    'ContentType': 'text/plain'
                }  
        }, ],
        LoadBalancerArn=elb['LoadBalancers'][0]['LoadBalancerArn'],
        Port=80,
        Protocol='HTTP',
    )

    response = ELB_CLIENT.create_rule(
        ListenerArn=listener['Listeners'][0]['ListenerArn'],
        Priority=1,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn':tg1_arn,
            }
        ],
        Conditions=[
            {
            'Field': 'path-pattern',
            'Values': ['/cluster1']
            }
        ]
    )
    
    response = ELB_CLIENT.create_rule(
        ListenerArn=listener['Listeners'][0]['ListenerArn'],
        Priority=2,
        Actions=[
            {
                'Type': 'forward',
                'TargetGroupArn':tg2_arn,
            }
        ],
        Conditions=[
            {
            'Field': 'path-pattern',
            'Values': ['/cluster2']
            }
        ]
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
        print(f'Security group already exists with id {security_group_id}.')
    except ClientError as e:
        print(e)
        exit(1)

# Create instances with the created security group rules
print('CREATING M4 INSTANCES ASSOCIATED WITH THE SECURITY GROUP')
m4_instance_type = 't2.nano'  # change to m4.large
m4_instances = create_ec2(M4_NUM_INSTANCES, m4_instance_type, security_group_id)

# Create instances with the created security group rules
print('CREATING T2 INSTANCES ASSOCIATED WITH THE SECURITY GROUP')
t2_instance_type = 't2.micro'  # change to t2.xlarge
t2_instances = create_ec2(T2_NUM_INSTANCES, t2_instance_type, security_group_id)

# Create a target group for the M4 instances created
print('CREATING A TARGET GROUP FOR THE M4 INSTANCES AND REGISTERING THEM')
m4_group_name = 'm4-Group'
m4_group_arn = create_tg(m4_group_name, vpc_id, m4_instances)


# Create a target group for the T2 instances created
print('CREATING A TARGET GROUP FOR THE T2 INSTANCES AND REGISTERING THEM')
t2_group_name = 't2-Group'
t2_group_arn = create_tg(t2_group_name, vpc_id, t2_instances)

# Create a load balancer for the target groups created
print('CREATING LOAD BALANCER AND ATTACHING IT TO M4 and T2 TARGET GROUPS')
elb_name = 'Lab1-load-balancer'
create_elb(elb_name, m4_group_arn, t2_group_arn, security_group_id)

# metrics analysis
# see the second file. We just need the instances ids and the target group ids.
instance_ids = [instance.id for instance in m4_instances]
instance_ids.extend([instance.id for instance in t2_instances])
with open("instance_ids.txt", "w") as f:
    f.write("\n".join(instance_ids))
    print("Wrote instance ids to instance_ids.txt")

tg_ids = [t2_group_arn.split(':')[-1], m4_group_arn.split(':')[-1]]
with open("tg_ids.txt", "w") as f:
    f.write("\n".join(tg_ids))
    print("Wrote target groups ids to tg_ids.txt")

# print('DELETE LOAD BALANCER')
# ELB_CLIENT.delete_load_balancer(LoadBalancerArn=m4_group_arn)
# print('STOPPING INSTANCES')
# EC2_CLIENT.terminate_instances(InstanceIds=[i.id for i in m4_instances])

import boto3
from botocore.exceptions import ClientError

# Sets up a security group, and creates an instance associated with it.
EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')
ELB_CLIENT = boto3.client('elbv2')

#Function to create {num_instances} amount of {instance_type} instances
#Returns a list of instance objects
def create_instances(
    num_instances, 
    instance_type):
    instances = EC2_RESOURCE.create_instances(
        ImageId='ami-0149b2da6ceec4bb0', # ubuntu 20.04 x86 (free) (the one we used in the first lab session iirc)
        MinCount=num_instances,
        MaxCount=num_instances,
        InstanceType=instance_type, # we will change accordingly (this one is free)
        SecurityGroupIds=[security_group_id], # we use the security group id just created above.
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': instance_type +'lab1-ec2-instance'
                    },
                ]
            },
        ]
        )
    print(f'{instances} are starting')
    return instances

#Function to create a target group called {group_name} that includes {instances}
#Returns __
def create_target_group(group_name, vpc_id, instances):
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
                'FromPort': 80,
                'ToPort': 80,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            {'IpProtocol': 'tcp',
                'FromPort': 443,
                'ToPort': 443,
                'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
                # TODO maybe we should add ssh redirection ?
        ]
    data = EC2_CLIENT.authorize_security_group_ingress(GroupId=security_group_id, IpPermissions=sec_group_rules)   
    print(f'Successfully updated security group rules with : {sec_group_rules}')
except ClientError as e:
    try: #if security group exists already, find the security group id
        response = EC2_CLIENT.describe_security_groups(
        Filters=[
            dict(Name='group-name', Values=[sec_group_name])
        ])
        security_group_id = response['SecurityGroups'][0]['GroupId']
        print(e)
    except ClientError as e:
        print(e)


print('CREATING AN INSTANCE ASSOCIATED WITH THE SECURITY GROUP')

num_instances = 1 #number of instances to create
instance_type = 't2.nano' #change to m4.large
m4_instances = create_instances(num_instances, instance_type)

#Create a target group for the instances created
print('CREATING A TARGET GROUP FOR THE M4 INSTANCES AND REGISTERING THEM')
m4_group_name = 'm4-Group'
create_target_group(m4_group_name, vpc_id, m4_instances)

# Sets up a security group, and creates an instance associated with it.

import boto3
from botocore.exceptions import ClientError

EC2_CLIENT = boto3.client('ec2')
EC2_RESOURCE = boto3.resource('ec2')

response = EC2_CLIENT.describe_vpcs()

# get our virtual cloud id
vpc_id = response.get('Vpcs', [{}])[0].get('VpcId', '')

print('CREATING SECURITY GROUP')
try:
    response = EC2_CLIENT.create_security_group(
        GroupName='lab1-security-group',
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
    data = EC2_CLIENT.authorize_security_group_ingress(
        GroupId=security_group_id,
        IpPermissions=sec_group_rules
    )
    print(f'Successfully updated security group rules with : {sec_group_rules}')
except ClientError as e:
    print(e)


print('CREATING AN INSTANCE ASSOCIATED WITH THE SECURITY GROUP')
instance = EC2_RESOURCE.create_instances(
    ImageId='ami-0149b2da6ceec4bb0', # ubuntu 20.04 x86 (free) (the one we used in the first lab session iirc)
    MinCount=1,
    MaxCount=1,
    InstanceType='t2.nano', # we will change accordingly (this one is free)
    SecurityGroupIds=[security_group_id], # we use the security group id just created above.
    TagSpecifications=[
        {
            'ResourceType': 'instance',
            'Tags': [
                {
                    'Key': 'Name',
                    'Value': 'lab1-ec2-instance'
                },
            ]
        },
    ]
)
print(f'{instance} is starting')

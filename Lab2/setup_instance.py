import boto3
from botocore.exceptions import ClientError
from os import path

EC2_RESOURCE = boto3.resource('ec2')
EC2_CLIENT = boto3.client('ec2')


def create_ec2(instance_type, sg_id, key_name):
    """Creates an EC2 instance

    Args:
        instance_type (str): Instance type (m4.large, ...)
        sg_id (str): Security group ID
        key_name (str): SSH key name

    Returns:
        instance: The created instance object
    """
    instance = EC2_RESOURCE.create_instances(
        ImageId='ami-0149b2da6ceec4bb0',
        MinCount=1,
        MaxCount=1,
        InstanceType=instance_type,
        Monitoring={'Enabled': True},
        SecurityGroupIds=[sg_id],
        KeyName=key_name,
        TagSpecifications=[
            {
                'ResourceType': 'instance',
                'Tags': [
                    {
                        'Key': 'Name',
                        'Value': 'lab2-hadoop-instance'
                    },
                ]
            },
        ]
    )[0]
    print(f'{instance} is starting')
    return instance


def create_security_group():
    """Creates a security group for the lab 2 needs

    Returns:
        security_group_id: The created security group ID
    """
    sec_group_name = 'lab2-security-group'
    security_group_id = None
    try:
        response = EC2_CLIENT.create_security_group(
            GroupName=sec_group_name,
            Description='Security group for the ec2 instances used in Lab1',
            # VpcId=vpc_id
        )
        security_group_id = response['GroupId']
        print(f'Successfully created security group {security_group_id}')
        sec_group_rules = [
            {'IpProtocol': 'tcp',
             'FromPort': 22,
             'ToPort': 22,
             'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            # {'IpProtocol': 'tcp',
            # 'FromPort': 80,
            # 'ToPort': 80,
            # 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]},
            # {'IpProtocol': 'tcp',
            # 'FromPort': 443,
            # 'ToPort': 443,
            # 'IpRanges': [{'CidrIp': '0.0.0.0/0'}]}
        ]
        data = EC2_CLIENT.authorize_security_group_ingress(GroupId=security_group_id,
                                                           IpPermissions=sec_group_rules)
        print(f'Successfully updated security group rules with : {sec_group_rules}')
        return security_group_id
    except ClientError as e:
        try:  # if security group exists already, find the security group id
            response = EC2_CLIENT.describe_security_groups(
                Filters=[
                    dict(Name='group-name', Values=[sec_group_name])
                ])
            security_group_id = response['SecurityGroups'][0]['GroupId']
            print(f'Security group already exists with id {security_group_id}.')
            return security_group_id
        except ClientError as e:
            print(e)
            exit(1)


def create_private_key_filename(key_name):
    """Generates a filename to save the key pair

    Args:
        key_name (str): key name

    Returns:
        str: Private key filename
    """
    return f'./private_key_{key_name}.pem'


def create_key_pair(key_name, private_key_filename):
    """Generates a key pair to access our instance

    Args:
        key_name (str): key name
        private_key_filename (str): filename to save the private key to
    """
    # TODO check if the key already exists distantlx
    print(f'Creating {private_key_filename}')
    if path.exists(private_key_filename):
        print(f'Private key {private_key_filename} already exists, use this file.')
        return

    response = EC2_CLIENT.create_key_pair(KeyName=key_name)
    with open(private_key_filename, 'w+') as f:
        f.write(response['KeyMaterial'])
    print(f'{private_key_filename} written.')


def retrieve_instance_ip(instance_id):
    """Retrieves an instance's public IP

    Args:
        instance_id (str): instance id

    Returns:
        str: Instance's public IP
    """
    print(f'Retrieving instance {instance_id} public IP...')
    instance_config = EC2_CLIENT.describe_instances(InstanceIds=[instance_id])
    instance_ip = instance_config["Reservations"][0]['Instances'][0]['PublicIpAddress']
    print(f'Public IP : {instance_ip}')
    return instance_ip


def start_instance():
    # Create the instance with the key pair
    instance = create_ec2('m4.large', sg_id, key_name)
    print(f'Waiting for instance {instance.id} to be running...')
    instance.wait_until_running()
    # Get the instance's IP
    instance_ip = retrieve_instance_ip(instance.id)

    with open('env_variables.txt', 'w+') as f:
        f.write(f'INSTANCE_IP={instance_ip}\n')
        f.write(f'PRIVATE_KEY_FILE={private_key_filename}\n')
    print('Wrote instance\'s IP and private key filename to env_variables.txt')
    print(f'Instance {instance.id} started. Access it with \'ssh -i {private_key_filename} ubuntu@{instance_ip}\'')


if __name__ == "__main__":
    # Create a key pair
    key_name = 'LAB2_KEY'
    private_key_filename = create_private_key_filename(key_name)
    create_key_pair(key_name, private_key_filename)

    # Create a security group
    sg_id = create_security_group()
    start_instance()






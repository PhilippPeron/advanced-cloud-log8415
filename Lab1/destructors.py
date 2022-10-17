import aws_constants
from botocore.exceptions import WaiterError

INSTANCE_STATE_NAME_QUERY_FIELD = 'instance-state-name'
INSTANCE_STATE_NAME_RUNNING_VALUE = 'running'
DESCRIBE_INSTANCES_RESERVATIONS_DICT_KEY = 'Reservations'
RESERVATIONS_INSTANCES_DICT_KEY = 'Instances'
INSTANCES_IDS_DICT_KEY = 'InstanceId'
DESCRIBE_LB_LB_KEY = 'LoadBalancers'
LB_ARN_DICT_KEY = 'LoadBalancerArn'


def terminate_running_instances(instances_ids):
    print('STOPPING INSTANCES WITH IDs : ' + str(instances_ids))
    terminate_instances_responses = aws_constants.EC2_CLIENT.terminate_instances(
        InstanceIds=instances_ids,
    )


def delete_load_balancers(load_balancer_arn=None):
    if load_balancer_arn is None:
        load_balancer_arn = []

    response = aws_constants.ELB_CLIENT.describe_load_balancers(
        LoadBalancerArns=load_balancer_arn,
    )
    load_balancers = response[DESCRIBE_LB_LB_KEY]

    for load_balancer in load_balancers:
        curr_lb_arn = load_balancer[LB_ARN_DICT_KEY]
        print('DELETE LOAD BALANCERS with ARNs: ' + curr_lb_arn)
        aws_constants.ELB_CLIENT.delete_load_balancer(
            LoadBalancerArn=curr_lb_arn
        )
        waiter = aws_constants.ELB_CLIENT.get_waiter('load_balancers_deleted')
        waiter.wait(
            LoadBalancerArns=[curr_lb_arn],
            WaiterConfig={
                'Delay': 10,
                'MaxAttempts': 100
            }
        )


def delete_target_groups(target_groups_arn=None):
    if target_groups_arn is None:
        target_groups_arn = []

    for target_group_arn in target_groups_arn:
        aws_constants.ELB_CLIENT.delete_target_group(
            TargetGroupArn=target_group_arn
        )
        print('DELETE TARGET GROUP with ARN: ' + target_group_arn)


def delete_security_groups(security_groups_ids=None):
    if security_groups_ids is None:
        security_groups_ids = []

    for security_group_id in security_groups_ids:
        aws_constants.EC2_CLIENT.delete_security_group(
            GroupId=security_group_id
        )
        print('DELETE SECURITY GROUP with ID: ' + security_group_id)


import aws_constants

INSTANCE_STATE_NAME_QUERY_FIELD = 'instance-state-name'
INSTANCE_STATE_NAME_RUNNING_VALUE = 'running'
DESCRIBE_INSTANCES_RESERVATIONS_DICT_KEY = 'Reservations'
RESERVATIONS_INSTANCES_DICT_KEY = 'Instances'
INSTANCES_IDS_DICT_KEY = 'InstanceId'


def terminate_all_running_instances():
    response = aws_constants.EC2_CLIENT.describe_instances(
        Filters=[
            {
                'Name': INSTANCE_STATE_NAME_QUERY_FIELD,
                'Values': [
                    INSTANCE_STATE_NAME_RUNNING_VALUE,
                ]
            },
        ],
    )
    reservations = response[DESCRIBE_INSTANCES_RESERVATIONS_DICT_KEY]
    instances_ids = []
    for reservation in reservations:
        instances = reservation[RESERVATIONS_INSTANCES_DICT_KEY]
        for instance in instances:
            instance_id = instance[INSTANCES_IDS_DICT_KEY]
            instances_ids.append(instance_id)

    terminate_instances_responses = aws_constants.EC2_CLIENT.terminate_instances(
        InstanceIds=instances_ids,
    )
    print(terminate_instances_responses)

terminate_all_running_instances()

from fileinput import filename
import boto3

import aws_constants


def save_metric(metric_config, file_name):
    response = aws_constants.CLOUDWATCH_CLIENT.get_metric_widget_image(MetricWidget=str(metric_config),
                                                                       OutputFormat="png")

    with open(file_name, "wb") as f:
        f.write(response["MetricWidgetImage"])
    print(f"Saved: {file_name}")


def main(instances_ids):
    metric_cpu_usage_all_instances = """{
        "metrics": [
    INSTANCE_IDS_PLACEHOLDER
        ],
        "view": "timeSeries",
        "stacked": false,
        "title": "CPU Utilization (%)",
        "stat": "Average",
        "period": 300,
        "width": 800,
        "height": 400,
        "start": "-PT45M",
        "end": "P0D"
    }"""

    instance_metric_conf = ''
    for tg_idx in range(len(instances_ids)):
        instance_metric_conf += f'[ "AWS/EC2", "CPUUtilization", "InstanceId", "{instances_ids[tg_idx]}" ]'
        if tg_idx < len(instances_ids) - 1:
            instance_metric_conf += ',\n'

    metric_cpu_usage_all_instances = metric_cpu_usage_all_instances.replace('INSTANCE_IDS_PLACEHOLDER',
                                                                            instance_metric_conf)

    metric_requests_per_tg = """{
        "view": "timeSeries",
        "stacked": false,
        "metrics": [
    TG_IDS_PLACEHOLDER
        ],
        "title": "Requests Count for the two target groups",
        "width": 800,
        "height": 400,
        "start": "-PT45M",
        "end": "P0D"
    }"""

    tg_metric_conf = ''
    for tg_idx in range(len(instances_ids)):
        tg_metric_conf += f'[ "AWS/ApplicationELB", "RequestCountPerTarget", "TargetGroup", "{instances_ids[tg_idx]}" ]'
        if tg_idx < len(instances_ids) - 1:
            tg_metric_conf += ',\n'

    metric_requests_per_tg = metric_requests_per_tg.replace('TG_IDS_PLACEHOLDER', tg_metric_conf)

    save_metric(metric_cpu_usage_all_instances, "cpu_usage_all_instances.png")
    save_metric(metric_requests_per_tg, "requests_per_tg.png")

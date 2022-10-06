from fileinput import filename
import boto3

CLOUDWATCH_CLIENT = boto3.client('cloudwatch')

def save_metric(metric_config, file_name):

    response = CLOUDWATCH_CLIENT.get_metric_widget_image(MetricWidget=str(metric_config), OutputFormat="png")

    with open(file_name, "wb") as f:
        f.write(response["MetricWidgetImage"])
    print(f"Saved: {file_name}")

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

with open("instance_ids.txt", "r") as f:
    ids = f.read().splitlines()

instance_metric_conf = ''
for tg_idx in range(len(ids)):
    instance_metric_conf += f'[ "AWS/EC2", "CPUUtilization", "InstanceId", "{ids[tg_idx]}" ]'
    if tg_idx < len(ids) - 1:
        instance_metric_conf += ',\n'

metric_cpu_usage_all_instances = metric_cpu_usage_all_instances.replace('INSTANCE_IDS_PLACEHOLDER', instance_metric_conf)

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

with open("tg_ids.txt", "r") as f:
    tg_ids = f.read().splitlines()

tg_metric_conf = ''
for tg_idx in range(len(ids)):
    tg_metric_conf += f'[ "AWS/ApplicationELB", "RequestCountPerTarget", "TargetGroup", "{ids[tg_idx]}" ]'
    if tg_idx < len(ids) - 1:
        tg_metric_conf += ',\n'

metric_requests_per_tg = metric_requests_per_tg.replace('TG_IDS_PLACEHOLDER', tg_metric_conf)

save_metric(metric_cpu_usage_all_instances, "cpu_usage_all_instances.png")
save_metric(metric_requests_per_tg, "requests_per_tg.png")

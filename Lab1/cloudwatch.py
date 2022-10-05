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
        [ "AWS/EC2", "CPUUtilization", "InstanceId", "i-05e4bfe3a8934b0ae" ],
        [ "...", "i-0147126bd9a1284d9" ],
        [ "...", "i-0d29e617f6d730752" ],
        [ "...", "i-0d62feaa5e77c3579" ],
        [ "...", "i-0b044427f4e479b76" ],
        [ "...", "i-01c5cac4516d0b72d" ],
        [ "...", "i-0271c9580485b1d3e" ],
        [ "...", "i-0da6b13604419447b" ],
        [ "...", "i-0281e18230ff9e554" ]
    ],
    "view": "timeSeries",
    "stacked": false,
    "title": "CPU Utilization ()",
    "stat": "Average",
    "period": 300,
    "width": 800,
    "height": 400,
    "start": "-PT45M",
    "end": "P0D"
}"""

metric_requests_per_tg = """{
    "view": "timeSeries",
    "stacked": false,
    "metrics": [
        [ "AWS/ApplicationELB", "RequestCountPerTarget", "TargetGroup", "targetgroup/m4-Group/85d4b2a89b3643e3" ],
        [ "...", "targetgroup/t2-Group/f25e0f7a0271a7be" ]
    ],
    "title": "Requests Count for the two target groups",
    "width": 800,
    "height": 400,
    "start": "-PT45M",
    "end": "P0D"
}"""

save_metric(metric_cpu_usage_all_instances, "cpu_usage_all_instances.png")
save_metric(metric_requests_per_tg, "requests_per_tg.png")

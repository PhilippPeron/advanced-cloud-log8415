import json
import requests
import numpy as np


def call_endpoint_http(cluster):
    url = f"http://lab1-load-balancer-1432216610.us-east-1.elb.amazonaws.com/{cluster}"
    headers = {"content-type": "application/text"}
    r = requests.get(url=url, headers=headers)
    return r.status_code, r.text


def print_benchmark_stats(stats):
    cluster1_ids, cluster1_counts = np.unique([s.split('Instance ')[1].split(' is ')[0] for s in stats["cluster1"]["responses"]], return_counts=True)
    cluster2_ids, cluster2_counts = np.unique([s.split('Instance ')[1].split(' is ')[0] for s in stats["cluster2"]["responses"]], return_counts=True)
    print("\n/cluster1 :")
    for i in range(len(cluster1_ids)):
        print(f"{cluster1_ids[i]} answered successfully {cluster1_counts[i]} requests")
    print(f"Total successful requests : {sum(cluster1_counts)}")
    print("\n/cluster2 :")
    for i in range(len(cluster2_ids)):
        print(f"{cluster2_ids[i]} answered successfully {cluster2_counts[i]} requests")
    print(f"Total successful requests : {sum(cluster2_counts)}")

stats = {
    "cluster1": {
        "responses": []
    },
    "cluster2": {
        "responses": []
    }
}


n_requests = 1000
for i in range(n_requests):
    try:
        print(f"Making request #{i} to cluster 1...")
        sc_1, resp_1 = call_endpoint_http("cluster1")
        if sc_1 == 200:
            stats["cluster1"]["responses"].append(resp_1)
    except Exception as e:
        print("An error occured while making a request to cluster 1")
        print(e)
    try:
        print(f"Making request #{i} to cluster 2...")
        sc_2, resp_2 = call_endpoint_http("cluster2")
        if sc_2 == 200:
            stats["cluster2"]["responses"].append(resp_2)
    except Exception as e:
        print("An error occured while making a request to cluster 2")
        print(e)

print_benchmark_stats(stats)

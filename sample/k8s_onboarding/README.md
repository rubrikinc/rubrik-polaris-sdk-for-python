# Kubernetes onboarding sample

This sample shows how the Python SDK can be used to onboard multiple on prem kubernetes clusters
including assigning a default SLA.

## Usage

Install required dependencies if not present already:
```
$ pip install -r requirements.txt
```

Create an input file accoding to [the input format](#input-file).

Run `python onboard.py -k polaris-service-account.json -i input.csv` to validate the input file.
Validations:
- input file format
- name uniqueness
- Polaris connectivity
- kubectl context existence
- CDM clusters existence
- SLAs existence

If validation pass, add `--create-clusters` and run again to create all k8s clusters, e.g.:
```
$ python onboard.py -k polaris-service-account.json -i input.csv --create-clusters
```

This will:
1. Create each k8s cluster in Polaris and apply the manifest using `kubectl`
2. Refresh each created k8s cluster to ensure it is connected before assigning SLA
3. Assign corresponding SLA to each k8s cluster

## Input file
The input file is a csv-file (tab separated with header row) with the following columns:
| Column name | Description | Example |
|--|--|--|
| NAME | Name of Kubernetes Cluster to use in Polaris (unique) | my_k8s_cluster |
| IPADDRESSES | Comma-separated list of IPs/hostnames of the k8s nodes | 10.2.3.4 |
| PORT | Port on the k8s node for the kupr Ingress Controller | 30000 |
| RBSPORTS | Comma-separated range of ports for RBS data traffic | 30100,30200 |
| KUBECONTEXT | kubectl Kubernetes context with access to apply manifest | kubectx |
| SLANAME | Name of SLA to assign as default to the created k8s cluster | Silver |

```
$ cat input.csv
NAME	IPADDRESSES	PORT	RBSPORTS	CDMCLUSTERNAME	KUBECONTEXT	SLANAME
my-k8s-1	10.1.0.10	32001	32101,32200	cdm-cluster-foo	my_kubectx	Bronze
my-k8s-2	10.2.0.20	32002	32201,32300	cdm-cluster-bar	other_kubectx	Silver
my-k8s-3	10.3.0.30,10.3.0.31,10.3.0.32	32003	32301,32400	cdm-cluster-foo	third_kubectl	Gold
```

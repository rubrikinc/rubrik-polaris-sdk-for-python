#!/usr/bin/env python
import argparse
import uuid
import sys
import subprocess
from typing import List

from kubernetes import config
import pandas as pd
from tenacity import retry, stop_after_delay, wait_exponential

from rubrik_polaris.rubrik_polaris import PolarisClient


class ValidationException(Exception):
    """ Exception during validation """
    pass


def main(raw_data: pd.DataFrame, rubrik: PolarisClient, dry_run: bool = True):
    try:
        # Ensure input format is valid and both specified k8s contexts as well
        # as CDM clusters exist.
        _validate_input(raw_data)
        _validate_kubecontext(list(raw_data.KUBECONTEXT.unique()))
        cdm_cluster_id = _cdm_cluster_map(rubrik)
        _validate_cdm_cluster_map(list(cdm_cluster_id), list(raw_data.CDMCLUSTERNAME))
        sla_id = _sla_name_map(rubrik)
        _validate_sla_map(list(sla_id), list(raw_data.SLANAME))

        # Ensure that kubectl is runnable. The k8s SDK for python doesn't support
        # the equivalent of "kubectl apply -f https://.." so we use kubectl.
        ctx = raw_data.iloc[0].KUBECONTEXT
        res = subprocess.run(["kubectl", "version", "--context", ctx], capture_output=True)
        if res.returncode != 0:
            raise ValidationException(f"failed to run 'kubectl version --context {ctx}':\n{res.stderr.decode()}")

        # Get k8s clusters already added in previous runs since  we shouldn't try to
        # add them again. They might be in an incomplete state where they need to
        # be either refreshed or both refreshed and SLA assigned.
        existing_k8s_clusters = rubrik.list_k8s_clusters()
        existing_k8s_cluster_names = []
        to_refresh = {}
        to_sla_assign = {}
        for cluster in existing_k8s_clusters:
            existing_k8s_cluster_names.append(cluster['name'])
            # Clusters with SLA assignment is considered "done".
            if cluster['slaAssignment'] != 'Unassigned':
                continue

            # We must ensure that pre-existing k8s clusters w/o SLA exist in the
            # input data since we need to know which SLA to assign.
            if len(raw_data.loc[raw_data.NAME == cluster['name']]) != 1:
                raise ValidationException(f'k8s cluster {cluster["name"]} without SLA exists in Polaris but not in input. Cannot determine SLA to assign')

            sla = raw_data.loc[raw_data.NAME == cluster['name']].squeeze().SLANAME
            if cluster['status'] == 'STATUS_INIT':
                to_refresh[cluster['id']] = sla
            elif cluster['slaAssignment'] == 'Unassigned':
                to_sla_assign[cluster['id']] = sla
    except ValidationException as e:
        print(f"validation failed: {e}")
        sys.exit(1)

    if dry_run:
        print("validation passed")
        return

    # Create all clusters that doesn't exist
    for i in range(len(raw_data)):
        row = raw_data.loc[i]

        if row.NAME in existing_k8s_cluster_names:
            print(f'skipped creating k8s cluster "{row.NAME}" since it already exist')
            continue

        rbsMinPort, rbsMaxPort = row.RBSPORTS.split(",")
        userMinPort, userMaxPort = row.USERPORTS.split(",")
        ips = [ip.strip() for ip in row.IPADDRESSES.split(",")]
        resp = rubrik.create_k8s_cluster(
            cdm_cluster_id[row.CDMCLUSTERNAME],
            ips,
            row.NAME,
            int(row.PORT),
            {
                "portMin": int(rbsMinPort),
                "portMax": int(rbsMaxPort),
            },
            {
                "portMin": int(userMinPort),
                "portMax": int(userMaxPort),
            },
            "ON_PREM"
        )

        _kubectl_apply(row.KUBECONTEXT, resp['yamlUrl'])
        to_refresh[resp['clusterId']] = row.SLANAME

    # Request refresh
    for k8s_cluster_id in to_refresh.keys():
        print(f"refreshing k8s cluster id {k8s_cluster_id}")
        _refresh_k8s_cluster(k8s_cluster_id)

        # The refresh can be successful even if the cluster wasn't connected so we need to
        # check the status explicitly afterwards
        status = rubrik.get_k8s_status(k8s_cluster_id)['status']
        if status != 'STATUS_CONNECTED':
            raise Exception(f'failed to connect k8s cluster {k8s_cluster_id}, status: {status}')
        sla_name = to_refresh[k8s_cluster_id]
        to_sla_assign[k8s_cluster_id] = sla_name

    # Assign default SLA
    for k8s_cluster_id in to_sla_assign.keys():
        sla_name = to_sla_assign[k8s_cluster_id]
        print(f'assigning SLA "{sla_name}" to k8s cluter {k8s_cluster_id}')
        rubrik.submit_assign_sla(k8s_cluster_id, sla_id[sla_name])


def _kubectl_apply(ctx: str, url: str):
    cmd = ["kubectl", "apply", "--context", ctx, "-f", url]
    print("running {}".format(' '.join(cmd)))
    res = subprocess.run(cmd, capture_output=True)
    if res.returncode != 0:
        raise Exception("failed to run '{}':\n{}".format(' '.join(cmd), res.stderr.decode()))


@retry(stop=stop_after_delay(600),
        wait=wait_exponential(multiplier=1, min=1, max=10),
        reraise=True)
def _refresh_k8s_cluster(k8s_cluster_id: uuid.UUID):
    resp = rubrik.refresh_k8s_cluster(k8s_cluster_id, wait=True)
    if resp['status'] == 'FAILED':
        raise Exception("refresh of k8s cluster with id {} failed:\n{}".format(k8s_cluster_id, resp))


def _validate_cdm_cluster_map(configured_cluster_names: List[str], input_cluster_names: List[str]):
    if len(configured_cluster_names) == 0:
        raise ValidationException("Found no CDM clusters")
    if not set(input_cluster_names).issubset(configured_cluster_names):
        missing = list(set(input_cluster_names) - set(configured_cluster_names))
        raise ValidationException('CDM cluster(s) "{}" in input do not exist in Polaris'.format(','.join(missing)))


def _validate_sla_map(configured_sla_names: List[str], input_sla_names: List[str]):
    if len(configured_sla_names) == 0:
        raise ValidationException("Found no SLA domains")
    if not set(input_sla_names).issubset(configured_sla_names):
        missing = list(set(input_sla_names) - set(configured_sla_names))
        raise ValidationException('SLA(s) "{}" in input do not exist in Polaris'.format(','.join(missing)))


def _validate_input(raw_data: pd.DataFrame):
    missing = {'NAME', 'IPADDRESSES', 'PORT', 'RBSPORTS', 'USERPORTS', 'CDMCLUSTERNAME', 'KUBECONTEXT', 'SLANAME'} - set(raw_data.columns)
    if len(missing) > 0:
        raise ValidationException(f'input file missing column(s) "{missing}"')
    if len(raw_data) == 0:
        raise ValidationException('input file has no rows')
    dups = raw_data.loc[raw_data.NAME.duplicated()]
    if len(dups) > 0:
        raise ValidationException(f'input has multiple lines with the same name:\n{dups}')


def _validate_kubecontext(contexts: List[str]):
    configured_contexts, active_context = config.list_kube_config_contexts()
    configured_context_names = [c['name'] for c in configured_contexts]
    if not set(contexts).issubset(configured_context_names):
        missing = list(set(contexts) - set(configured_context_names))
        raise ValidationException('kubectl context(s) "{}" in input not found'.format(','.join(missing)))


def _cdm_cluster_map(rubrik: PolarisClient) -> dict:
    cluster_map = {}
    for cluster in rubrik.list_clusters():
        cluster_map[cluster['name']] = cluster['id']
    return cluster_map


def _sla_name_map(rubrik: PolarisClient) -> dict:
    sla_map = {}
    for sla in rubrik.get_sla_domains():
        sla_map[sla['name']] = sla['id']
    return sla_map


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-p', '--password', dest='password', help="Polaris Password", default=None)
    parser.add_argument('-u', '--username', dest='username', help="Polaris UserName", default=None)
    parser.add_argument('-d', '--domain', dest='domain', help="Polaris Domain", default=None)
    parser.add_argument('-k', '--keyfile', dest='json_keyfile', help="JSON Keyfile", default=None)
    parser.add_argument('-r', '--root', dest='root_domain', help="Polaris Root Domain", default=None)
    parser.add_argument('--insecure', help='Deactivate SSL Verification', action="store_true")
    parser.add_argument('-i', '--input', dest='input_csv', help="Clusters CSV file", required=True)
    parser.add_argument('--create-clusters', dest='create_clusters', help="Create K8s clusters according to input", action="store_true")

    args = parser.parse_args()
    dry_run = not args.create_clusters

    try:
        if args.json_keyfile:
            rubrik = PolarisClient(json_keyfile=args.json_keyfile, insecure=args.insecure)
        else:
            rubrik = PolarisClient(domain=args.domain, username=args.username, password=args.password, root_domain=args.root_domain, insecure=args.insecure)
    except Exception as e:
        print(e)
        sys.exit(1)

    raw_data = pd.read_csv(args.input_csv, delimiter='\t')
    main(raw_data, rubrik, dry_run)

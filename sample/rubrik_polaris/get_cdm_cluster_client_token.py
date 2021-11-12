"""Create a CDM session on a given cluster with a Polaris service account,
and retrieve cluster info from the cluster.

This sample script takes its configuration from a yaml file,
see get_cdm_cluster_client_token.yaml for an example.
"""
import requests
from argparse import ArgumentParser
from rubrik_polaris import ServiceAccount
from pprint import PrettyPrinter
import urllib3
from pathlib import Path
from yaml import safe_load

if __name__ == '__main__':
    pp = PrettyPrinter(indent=4)
    parser = ArgumentParser()
    parser.add_argument('conf_file', type=Path,
                        help='Path to configuration file for this script.')
    parser.add_argument('-k', '--insecure', action="store_true", default=False,
                        help='Allow connections to be insecure.')
    args = parser.parse_args()
    conf = safe_load(args.conf_file.read_text())
    pp.pprint(conf)
    sa = ServiceAccount.from_json(conf['service_account'])
    session_id, token, expiration = \
        sa.get_cluster_client_token(conf['appliance']['cluster_uuid'])
    print(f'CDM Session:\n'
          f'  id: {session_id}\n'
          f'  token: {token}\n'
          f'  expiration: {expiration}')
    cluster_node = conf['appliance'].get('cluster_node')
    if cluster_node:
        if args.insecure:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
        cdm_url = f'http://{cluster_node}/api/v1/cluster/me'
        print(f'GET {cdm_url} :')
        r = requests.get(cdm_url,
                         headers={'Authorization': f'Bearer {token}'},
                         verify=not args.insecure)
        pp = PrettyPrinter(indent=4)
        pp.pprint(r.json())

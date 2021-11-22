"""Create a session token for a given appliance with a service account,
and retrieve cluster version string from the appliance API.

This sample script needs 3 pieces of information to run:
 1. the location of a service account JSON file (that you downloaded from
    the UI when creating a service account);
 2. the unique identifier of the appliance (typically, the cluster UUID);
 3. the appliance node IP (typically, a cluster node IP address).
"""
from argparse import ArgumentParser
from os import environ
from pathlib import Path
from typing import Union

import requests
import urllib3

import rubrik_polaris

# Try to use the Rubrik CDM Python SDK.
# If not on path, we fall back to a direct HTTP GET
# instead of a CDM SDK call.
try:
    import rubrik_cdm
except ImportError:
    rubrik_cdm = None


def get_cluster_ipaddr(sa: rubrik_polaris.ServiceAccount,
                       uuid: str) -> str:
    """Retrieve cluster IP address from the Rubrik GraphQL API.
    Raises if `uuid` is invalid, or refers to a
    disconnected cluster.
    """
    rubrik = rubrik_polaris.PolarisClient.from_service_account(sa)
    return rubrik.get_cdm_cluster_ipaddr(uuid)


def get_appliance_token(conf_file: Union[str, Path],
                        appliance_uuid: str,
                        insecure=False):
    # Create a service account from configuration:
    sa = rubrik_polaris.ServiceAccount.from_json_file(conf_file)

    # Retrieve appliance IP address from the GraphQL API:
    ipaddr = get_cluster_ipaddr(sa, appliance_uuid)

    # Retrieve an appliance token from the service account API:
    session_id, token, expiration = \
        sa.get_appliance_token(appliance_uuid)
    print(f'Appliance token:\n'
          f'  id: {session_id}\n'
          f'  token: {token}\n'
          f'  expiration: {expiration}\n')

    # Test the appliance token:
    # retrieve the version string from the cluster node:

    # Try to use the Rubrik CDM Python SDK:
    if rubrik_cdm:
        # Send request using Rubrik CDM Python SDK:
        environ['rubrik_cdm_node_ip'] = ipaddr
        environ['rubrik_cdm_token'] = token
        environ.pop('rubrik_cdm_username', None)
        environ.pop('rubrik_cdm_password', None)
        appliance = rubrik_cdm.Connect()
        print('rubrik_cdm.Connect().cluster_version()')
        cluster_version = appliance.cluster_version()
        print('Cluster version: ', cluster_version)
    else:
        # If Rubrik CDM Python SDK not on the path, send the request
        # directly with an HTTP GET:
        print('Rubrik CDM Python SDK not found on path.')
        appliance_url = f'http://{ipaddr}/api/v1/cluster/me/version'
        print(f'GET {appliance_url}')
        r = requests.get(appliance_url,
                         headers={'Authorization': f'Bearer {token}'},
                         verify=not insecure)
        print('Cluster version: ', r.json()['version'])


if __name__ == '__main__':
    parser = ArgumentParser(description=__doc__)
    parser.add_argument('conf_file', type=Path,
                        help='Path to service account JSON file.')
    parser.add_argument('uuid',
                        help='Appliance/cluster UUID')
    parser.add_argument('-k', '--insecure', action="store_true", default=False,
                        help='Allow connections to be insecure.')
    args = parser.parse_args()
    if args.insecure:
        urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    get_appliance_token(args.conf_file, args.uuid, args.insecure)

"""Create a CDM session on a given cluster with a Polaris service account,
and retrieve cluster info from the cluster.

This sample script takes its configuration from the environment.

Required environment variables:

 - 'rubrik_polaris_client_id' : service account client id.
   Example value:
   'client|rjSOLdenk7gtFWSnSiSgX4G1SprdkF6I'
 - 'rubrik_polaris_client_secret' : service account client secret.
   Example value:
   'qzY2TtYxPB0WYvqviWtHvK2w5P3wvQ39YXTPpIAEZCxLkSkfDCE0IV4DTWu3_o2S'
 - 'rubrik_cluster_uuid' : CDM cluster ID.
   Example value:
   '40505837-9772-4a91-a18a-db6108c66b59'
 - 'rubrik_domain' : Rubrik domain.
   Example value:
   'my-company'
 - 'rubrik_cdm_node' : CDM node host name or IP address.
   Example value:
   '10.20.30.40'
"""
import requests
import argparse
from rubrik_polaris import ServiceAccount

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('-c', '--cluster', dest='cluster',
                        help='Cluster UUID',
                        default=None)
    parser.add_argument('-n', '--node', dest='node',
                        help='Cluster node host name or IP address',
                        default=None)
    parser.add_argument('-f', '--file', dest='file',
                        help='Read service account from file',
                        default=None)
    args = parser.parse_args()
    if args.file:
        sa = ServiceAccount.from_json_file(args.file)
    else:
        sa = ServiceAccount.from_env()
    session_id, token, expiration = \
        sa.get_cluster_client_token(cluster_uuid=args.cluster)
    print(f'CDM Session:\n'
          f'  id: {session_id}\n'
          f'  token: {token}\n'
          f'  expiration: {expiration}')
    if args.node:
        cdm_url = f'https://{args.node}/api/v1/cluster/me'
        print(f'GET {cdm_url} :')
        r = requests.get(cdm_url, headers={'Authorization': f'Bearer {token}'})
        print(r.json())

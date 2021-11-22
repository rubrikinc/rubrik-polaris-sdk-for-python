# Copyright 2020 Rubrik, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.


"""
Collection of functions that manipulate CDM Cluster components
"""
from .exceptions import RequestException


def get_cdm_cluster_location(self, cluster_id):
    """Retrieves the location address for a CDM Cluster
    Args:
        cluster_id (str): The ID of a CDM cluster
    Returns:
        str: The Cluster location address
        str: Cluster location has not be configured.
        str: A cluster with an ID of {cluster_id} was not found.
    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "cdm_cluster_location"
        variables = {
            "filter": {
                "id": [cluster_id]
            }
        }
        query = self._query(query_name, variables)
        if query['nodes']:
            if query['nodes'][0]['geoLocation'] != None:
                return query['nodes'][0]['geoLocation']['address']
            else:
                return "No Location Configured"
        else:
            raise Exception("A CDM Cluster with an ID of {} was not found.".format(cluster_id))

    except Exception:
        raise


def get_cdm_cluster_connection_status(self, cluster_id):
    """Retrieves the Polaris connection status for a CDM Cluster
    Args:
        cluster_id (str): The ID of a CDM cluster
    Returns:
        str: The Cluster connection status.

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "cdm_cluster_connection_status"
        variables = {
            "filter": {
                "id": [cluster_id]
            }
        }
        query = self._query(query_name, variables)
        if query['nodes']:
            return query['nodes'][0]['state']['connectedState']
        else:
            raise Exception("A CDM Cluster with an ID of {} was not found.".format(cluster_id))

    except Exception:
        raise


def get_cdm_cluster_ipaddr(self, cluster_id: str) \
        -> str:
    """Retrieves a Cluster's first node's IP address.

    :param self:
    :param cluster_id: UUID of cluster.
    :return: The cluster IP address.
    :raise:
      - HTTPError if any exception occurred with the HTTP connection;
      - RequestException in 2 cases:
        - If the cluster ID wasn't found. Example of exception message:
            "Exception: Cluster with ID e3099370..9e93d52049 was not found."
       - If the cluster is not connected. Example of exception message:
            "Exception: Cluster with ID a34d5fbb..b3de90b54e is not connected."
    """
    query_name = "cdm_cluster_ipaddr"
    variables = {
        "filter": {
            "id": [cluster_id]
        }
    }
    query = self._query(query_name, variables)
    if query['nodes']:
        node = query['nodes'][0]
        if node['state']['connectedState'] != 'Connected':
            raise RequestException(f'Cluster with ID {cluster_id} is not connected.')
        return node['clusterNodeConnection']['nodes'][0]['ipAddress']
    else:
        raise RequestException(f'Cluster with ID {cluster_id} was not found.')

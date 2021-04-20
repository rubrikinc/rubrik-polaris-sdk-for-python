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
            print(query)
        else:
            raise Exception("A CDM Cluster with an ID of {} was not found.".format(cluster_id))
            
    except Exception:
        raise
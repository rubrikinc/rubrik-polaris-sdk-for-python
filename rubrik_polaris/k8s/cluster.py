# Copyright 2022 Rubrik, Inc.
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

from rubrik_polaris.exceptions import PolarisException

"""
Collection of functions related to kubernetes support.
"""


def create_k8s_cluster(
        self,
        cdm_cluster_id,
        host_list,
        k8s_cluster_name,
        kupr_ingress_port,
        user_port_ranges,
        rbs_port_ranges,
        kupr_cluster_type,
        proxy_url = None

):
    """Add a Kubernetes cluster

    Args:
        cdm_cluster_id (uuid): The ID of the CDM cluster for ON_PREM k8s clusters.
        host_list (list): List of host IPs/hostnames of the k8s nodes.
        k8s_cluster_name (str): Name of the k8s cluster.
        kupr_ingress_port (int): Port on the k8s node for the kupr Ingress Controller.
        user_port_ranges (dict): Node port ranges dedicated for export operations.
        rbs_port_ranges (dict): Ports in the range of node port service range of the Kubernetes cluster.
        kupr_cluster_type (str): KuprClusterType of the k8s cluster.
        proxy_url (str): Proxy URL for egress calls into Polaris

    Returns:
        dict: Details of created k8s cluster in Polaris

    Raises:
        PolarisException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.create_k8s_cluster(  "b946faa1-ee98-4924-affb-9b4315686879", ["1.2.3.4", "1.2.3.5"], 30000, {"portMin": 30100, "portMax": 30200},  {"portMin": 30300, "portMax": 30400}, "ON_PREM" )
    """
    try:
        _query_name = "k8s_add"
        self._validate(
            mutation_name=_query_name,
            cdm_cluster_id=cdm_cluster_id,
            host_list=host_list,
            user_port_ranges=user_port_ranges,
            rbs_port_ranges=rbs_port_ranges,
            kupr_cluster_type=kupr_cluster_type,
        )
        _variables = {
            "cdm_cluster_id": self.cdm_cluster_id,
            "host_list": self.host_list,
            "k8s_cluster_name": k8s_cluster_name,
            "kupr_ingress_port": kupr_ingress_port,
            "user_port_ranges": [self.user_port_ranges],
            "rbs_port_ranges": [self.rbs_port_ranges],
            "cluster_type": self.kupr_cluster_type,
            "proxy_url": proxy_url
        }
        return self._query(self.mutation_name, _variables)
    except Exception as e:
        raise PolarisException("Failed to create cluster: {}".format(e))


def refresh_k8s_cluster(self, kupr_cluster_id, wait=False):
    """Refresh resources of a Kubernetes cluster.

    Args:
        kupr_cluster_id (uuid): The ID of the kupr cluster to be refreshed.
        wait (bool): Wait for taskchain completion before return

    Returns:
        dict: Details of the refresh job

    Raises:
        PolarisException: If the query to Polaris returned an error
    """
    try:
        _query_name = "k8s_refresh"
        self._validate(
            mutation_name=_query_name,
            kupr_cluster_id=kupr_cluster_id,
        )
        _variables = {
            "kupr_cluster_id": self.kupr_cluster_id
        }
        _response = self._query(self.mutation_name, _variables)
        if wait:
            return self._monitor_task({'taskchainUuid': _response.get('taskchainId')})
        return _response
    except Exception as e:
        raise PolarisException("Failed to refresh k8s cluster: {}".format(e))


def list_k8s_clusters(self):
    """List Kubernetes clusters.

    Args:

    Returns:
        list: List of kubernetes clusters

    Raises:
        PolarisException: If the query to Polaris returned an error
    """
    try:
        _query_name = "k8s_list"
        self._validate(
            query_name=_query_name,
        )
        return self._query(self.query_name)
    except Exception as e:
        raise PolarisException("Failed to list k8s clusters: {}".format(e))


def get_k8s_status(self, kupr_cluster_id):
    """Get k8s cluster status

    Args:
        kupr_cluster_id (uuid): The ID of the kupr cluster to be refreshed.

    Returns:
        dict: Kubernetes cluster status

    Raises:
        PolarisException: If the query to Polaris returned an error
    """
    try:
        _query_name = "k8s_status"
        self._validate(
            query_name=_query_name,
            kupr_cluster_id=kupr_cluster_id,
        )
        _variables = {
            "kupr_cluster_id": self.kupr_cluster_id,
        }
        return self._query(self.query_name, _variables)
    except Exception as e:
        raise PolarisException("Failed to get k8s cluster status: {}".format(e))

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


def get_k8s_namespaces(self, query_filter=None):
    """Get all k8s namespaces

    Args:

    Returns:
        list: Kubernetes namespaces

    Raises:
        PolarisException: If the query to Polaris returned an error
    """
    try:
        _query_name = "k8s_namespaces"
        self._validate(
            query_name=_query_name,
        )
        _variables = {
            "filter": query_filter,
        }
        _request = self._query(self.query_name)
        return _request
    except Exception as e:
        raise PolarisException("Failed to create cluster: {}".format(e))


def get_k8s_namespace(self, polaris_id):
    """Get k8s namespace

    Args:
        polaris_id (uuid): The Polaris UUID for the object.

    Returns:
        dict: Kubernetes namespace details

    Raises:
        PolarisException: If the query to Polaris returned an error
    """
    try:
        _query_name = "k8s_namespaces"
        self._validate(
            query_name=_query_name,
        )
        _variables = {
            "polaris_id": polaris_id,
        }
        _request = self._query(self.query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Failed to create cluster: {}".format(e))

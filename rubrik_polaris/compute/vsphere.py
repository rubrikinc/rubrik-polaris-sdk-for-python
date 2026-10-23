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
Collection of functions that manipulate vSphere compute components
"""

def get_compute_vsphere(self, filter=None):
    """Retrieves all VMware VM object details and implements gql filter (Under development)

    Args:
        filter (dict): Limit of results to retrieve. Uses GQL filter (ex- [{"field": "NAME", "texts": ["100gb-centos-001"]}])

    Returns:
        dict: details of VMware VM objects

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "compute_vmware_vsphere_list"
        # self._validate(
        #     query_name=query_name
        # )
        variables = {"filter": filter, "first": 500}
        return self._query(query_name, variables)
    except Exception:
        raise

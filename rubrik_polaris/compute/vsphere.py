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

def get_compute_object_ids_vsphere(self, match_all=True, **kwargs):
    """Retrieves all vSphere objects that match query

    Arguments:
        match_all {bool} -- Set to false to match ANY defined criteria
        kwargs {} -- Any top level object from the get_compute_ec2 call
    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        object_ids = []
        num_criteria = len(kwargs)
        for instance in self.get_compute_vsphere():
            num_unmatched_criteria = num_criteria
            for key in kwargs:
                if key in instance and instance[key] == kwargs[key]:
                    num_unmatched_criteria -= 1
            if match_all and num_unmatched_criteria == 0:
                object_ids.append(instance['id'])
            elif not match_all and num_criteria > num_unmatched_criteria >= 1:
                object_ids.append(instance['id'])
        return object_ids
    except Exception:
        raise


def get_compute_vsphere(self):
    """Retrieves all VMware VM object details (Under development)

    Returns:
        dict: details of VMware VM objects

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "compute_vmware_vsphere"
        # self._validate(
        #     query_name=query_name
        # )
        variables = {"filter": [], "first": 500}
        return self._query(query_name, variables)
    except Exception:
        raise
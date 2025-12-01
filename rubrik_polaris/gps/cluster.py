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
Constants
"""
ERROR_MESSAGES = {
    'INVALID_FIELD_TYPE': "'{}' is an invalid value for '{}'. Value must be in {}.",
    'INVALID_FILTER': "'{}' is an invalid filter type."
}

"""
Collection of methods for GPS clusters.
"""


def list_clusters(self, first: int = None, after: str = None, filters: dict = None, sort_by: enumerate = None,
                  sort_order: enumerate = None):
    """
    Retrieves a list of available clusters.
    Args:
        after: The next page cursor to retrieve the next set of results.
        first : Number of results to retrieve in the response.
        filters: Filters the cluster result. Supported fields of class ClusterFilterInput.
        sort_by: Sorts the result using ClusterSortByEnum.
        sort_order: Sorting orders ASC or DESC.

    Returns:
        iterator: List of clusters.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error.

    """
    if filters is None:
        filters = {}
    try:
        variables = {
            'filter': filters
        }

        first = self.check_first_arg(first)
        if first:
            variables['first'] = first

        if after:
            variables['after'] = after.strip()

        if sort_by:
            supported_sla_sort_by = self.get_enum_values(name="ClusterSortByEnum")
            if sort_by not in supported_sla_sort_by:
                raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_by, 'sort_by', supported_sla_sort_by))

            variables['sortBy'] = sort_by

        if sort_order:
            supported_sla_sort_order = self.get_enum_values(name="SortOrder")
            if sort_order not in supported_sla_sort_order:
                raise ValueError(
                    ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_order, 'sort_order', supported_sla_sort_order))

            variables['sortOrder'] = sort_order

        return self._query_paginated(query_name="gps_clusters", variables=variables)
    except Exception:
        raise

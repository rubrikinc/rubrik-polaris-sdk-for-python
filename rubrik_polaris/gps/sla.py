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
}

"""
Collection of methods for GPS SLAs.
"""


def list_sla_domains(self, after: str = None, first: int = None, filters: list = None, sort_by: enumerate = None,
                    sort_order: enumerate = None, show_protected_object_count: bool = None):
    """
    Args:
        after: The next page cursor to retrieve the next set of results.
        first : Number of results to retrieve in the response.
        filters: Filters the SLA result. Supported fields of class GlobalSlaQueryFilterInputField.
        sort_by: Sorts the result using SLAQuerySortByFieldEnum.
        sort_order: Sorting orders ASC or DESC.
        show_protected_object_count: A Boolean option to return data with protected object count.

    Returns:
        dict: Dictionary containing list of SLAs.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error.
    """
    try:
        variables = {}

        first = self.check_first_arg(first)
        if first:
            variables['first'] = first

        if isinstance(filters, str):
            filters = [filters]

        if filters:
            for sla_filter in filters:
                if sla_filter.get("field", "") == "OBJECT_TYPE":
                    object_types = sla_filter.get("objectTypeList", [])
                    supported_object_types = self.get_enum_values(name="SLAObjectTypeEnum")
                    if not set(object_types).issubset(supported_object_types):
                        raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(object_types, "object types", supported_object_types))
            variables['filter'] = filters

        if after:
            variables['after'] = after.strip()

        if sort_by:
            supported_sla_sort_by = self.get_enum_values(name="SLAQuerySortByFieldEnum")
            if sort_by not in supported_sla_sort_by:
                raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_by, 'sort_by', supported_sla_sort_by))

            variables['sortBy'] = sort_by

        if sort_order:
            supported_sla_sort_order = self.get_enum_values(name="SLAQuerySortByOrderEnum")
            if sort_order not in supported_sla_sort_order:
                raise ValueError(
                    ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_order, 'sort_order', supported_sla_sort_order))

            variables['sortOrder'] = sort_order

        if show_protected_object_count:
            variables['shouldShowProtectedObjectCount'] = self.to_boolean(show_protected_object_count)

        return self._named_raw_query(query_name="gps_sla_domain", variables=variables)
    except Exception:
        raise

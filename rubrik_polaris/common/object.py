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
Collection of methods that are related to objects (virtual machines, filesets etc).
"""

ERROR_MESSAGES = {
    'INVALID_FIELD_TYPE': "'{}' is an invalid value for '{}'. Value must be in {}.",
    'INVALID_CLUSTER_CONNECTED': "'{}' is an invalid value for 'cluster_connected'. Value must be either boolean True or"
                                 " boolean False.",
    'INVALID_TIMEZONE_OFFSET': "'{}' is an invalid value for 'timezone_offset'. Value must be of type float.",
    'INVALID_FIRST': "'{}' is an invalid value for 'first'. Value must be an integer greater than 0.",
    'MISSING_PARAMETERS_IN_METADATA': 'object_id field is required.',
    'MISSING_PARAMETERS_IN_SNAPSHOT': 'object_id, snapshot_group_by, missed_snapshot_group_by, time_range, '
                                      'timezone_offset, and cluster_connected fields are required.',
    'SORT_FIELDS_REQUIRED': 'sort_by and sort_order both fields must be initialized or both must be uninitialized.'
}


def list_vm_objects(self, filters: list = None, first=20, sort_by: str = None,
                    sort_order: str = None, after: str = None):
    """Retrieve a list of all the objects of the VSphere Vm.

    Args:
        first (int): Limit of results to retrieve. Defaults to 20, if not provided.
        sort_by (str): Field to sort the results.
        sort_order (str): Sort order for the results.
        filters (list): Filter object.
        after (str): the cursor token to retrieve the next set of results.

    Returns:
        dict: Dictionary of VsphereVm objects

    Raises:
        RequestException: If the query to Polaris returned an error

    """
    if filters is None:
        filters = []
    try:
        if not first or (isinstance(first, int) and first <= 0):
            raise ValueError(ERROR_MESSAGES['INVALID_FIRST'].format(first))

        sort_by_enum = self.get_enum_values(name="HierarchySortByField")
        if sort_by and sort_by not in sort_by_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                sort_by, 'sort_by', sort_by_enum))

        sort_order_enum = self.get_enum_values(name="HierarchySortOrder")
        if sort_order and sort_order not in sort_order_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                sort_order, 'sort_order', sort_order_enum))

        query_name = "polaris_vm_object_list"
        variables = {"first": first, "filter": filters}
        if sort_by and sort_order:
            variables["sortBy"] = sort_by
            variables["sortOrder"] = sort_order
        if (sort_order and not sort_by) or (sort_by and not sort_order):
            raise ValueError(ERROR_MESSAGES['SORT_FIELDS_REQUIRED'])
        if after:
            variables["after"] = after

        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def search_object(self, filters: list = None, first: int = 20, sort_by: str = None, sort_order: str = None,
                  after: str = None):
    """
    Globally searches for objects on Rubrik Polaris platform

    Args:
        filters (list): A list of filters of type 'Filter' which include key fields field, texts, tagFilterParams,
                        objectTypeFiltersParams, awsNativeProtectionFeatureNames, isNegative and isSlowSearchEnabled.
        first (int): Number of objects to retrieve. Defaults to 20, if not provided.
        sort_by (str): the field to use for sorting the objects (Possible values can be obtained by querying the values
                        'HierarchySortByField' of Enum). If not provided, will return the default sorted response.
        sort_order (str): the order to sort objects in (Possible values 'ASC' and 'DESC'). If not provided, will return
                            the default sorted response.
        after (str): the cursor token to retrieve the next set of results.

    Returns:
        Dict: The global search results object

    Raises:
        RequestException: If the query to Polaris returned an error
        ValueError: if arguments are incorrect
    """
    try:
        if not first or (isinstance(first, int) and first <= 0):
            raise ValueError(ERROR_MESSAGES['INVALID_FIRST'].format(first))

        sort_by_enum = self.get_enum_values(name="HierarchySortByField")
        if sort_by and sort_by not in sort_by_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                sort_by, 'sort_by', sort_by_enum))

        sort_order_enum = self.get_enum_values(name="HierarchySortOrder")
        if sort_order and sort_order not in sort_order_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                sort_order, 'sort_order', sort_order_enum))

        query_name = "polaris_object_search"
        variables = {
            "filter": [] if not filters else filters,
            "first": first
        }
        if sort_by and sort_order:
            variables["sortBy"] = sort_by
            variables["sortOrder"] = sort_order
        if (sort_order and not sort_by) or (sort_by and not sort_order):
            raise ValueError(ERROR_MESSAGES['SORT_FIELDS_REQUIRED'])
        if after:
            variables["after"] = after

        return self._query_raw(query_name=query_name, variables=variables)
    except Exception:
        raise


def get_object_metadata(self, object_id):
    """
    Retrieve details for a Vsphere object based on the provided object ID.

    Args:
        object_id (str): The ID of the object to get details.
    Returns:
        dict: Response from the API.
    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        if not object_id:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_METADATA'])

        query_name = "polaris_vm_object_metadata"
        variables = {
            "id": object_id
        }
        query = self._query_raw(query_name=query_name, variables=variables)

        return query

    except Exception:
        raise


def get_object_snapshot(self, object_id, snapshot_group_by, missed_snapshot_group_by, time_range, timezone_offset,
                        cluster_connected):
    """
    Search for a Rubrik snapshot of an object based on the provided snapshot ID, exact timestamp, or specific value like
    earliest/latest, or closest before/after a timestamp.

    Args:
        object_id (str): The object ID for which the snapshots are to be searched.
        snapshot_group_by (str): Grouping the snapshots on the basis of the selected value.
                                Possible values are: "Month", "Day", "Year", "Week", "Hour", "Quarter".
        missed_snapshot_group_by (str): Grouping the missed snapshots on the basis of the selected value.
                                        Possible values are: "Month", "Day", "Year", "Week", "Hour", "Quarter".
        time_range (dict): The time range to get snapshots from and until.
        timezone_offset (float): The timezone offset from UTC changes to match the configured time zone.
                                Use this argument to filter the data according to the provided timezone offset.
                                Formats accepted: 1, 1.5, 2, 2.5, 5.5, etc
        cluster_connected (bool): Whether the cluster is connected or not. Possible values are: True, False.

    Returns:
        dict: Response from the API.
    Raises:
        RequestException: If the query to Polaris returned an error
    """

    try:

        if not object_id or not snapshot_group_by or not missed_snapshot_group_by or not time_range\
                or not timezone_offset or cluster_connected in ['', None]:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_SNAPSHOT'])

        snapshot_group_by_enum = self.get_enum_values(name="CdmSnapshotGroupByEnum")
        if snapshot_group_by not in snapshot_group_by_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                snapshot_group_by, 'snapshot_group_by', snapshot_group_by_enum))

        missed_snapshot_group_by_enum = self.get_enum_values(name="MissedSnapshotGroupByEnum")
        if missed_snapshot_group_by not in missed_snapshot_group_by_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                missed_snapshot_group_by, 'missed_snapshot_group_by', missed_snapshot_group_by_enum))

        if not isinstance(cluster_connected, bool):
            raise ValueError(ERROR_MESSAGES['INVALID_CLUSTER_CONNECTED'].format(cluster_connected))

        try:
            timezone_offset = float(timezone_offset)
        except Exception:
            raise ValueError(ERROR_MESSAGES['INVALID_TIMEZONE_OFFSET'].format(timezone_offset))

        query_name = "polaris_vm_object_snapshot"

        variables = {
            "id": object_id,
            "snapshotGroupBy": snapshot_group_by,
            "missedSnapshotGroupBy": missed_snapshot_group_by,
            "timeRange": time_range,
            "timezoneOffset": timezone_offset,
            "clusterConnected": cluster_connected
        }
        query = self._query_raw(query_name=query_name, variables=variables)

        return query

    except Exception:
        raise

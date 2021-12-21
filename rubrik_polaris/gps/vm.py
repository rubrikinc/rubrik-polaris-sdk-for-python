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
Collection of methods for live mount of a virtual machine.
"""

from typing import Union

ERROR_MESSAGES = {
    'INVALID_FIELD_TYPE': "'{}' is an invalid value for '{}'. Value must be in {}.",
    'REQUIRED_ARGUMENT': '{} field is required.',
    'REQUIRED_KEYS_IN_CONFIG': "Config field should contain datastoreId, hostId or clusterId and snapshotId.",
    'INVALID_CONFIG': "'{}' is an invalid value for field config."
}


def create_vm_livemount(self, snapshot_fid: str, host_id: str = None, vm_name: str = None, disable_network: bool = None,
                        remove_network_devices: bool = None, power_on: bool = None, keep_mac_addresses: bool = None,
                        data_store_name: str = None, create_data_store_only: bool = None, vlan: int = None,
                        should_recover_tags: bool = None):
    """
    Perform a live mount of a virtual machine snapshot.
    Args:
        snapshot_fid: The Snapshot FID of the snapshot.
        host_id: The Host ID.
        vm_name: The VM Name.
        disable_network: Whether to disable network.
        remove_network_devices: Whether to remove network devices.
        power_on: Whether to power on.
        keep_mac_addresses: Whether to keep MAC address.
        data_store_name: Name of the data store.
        create_data_store_only: Whether to create data store.
        vlan: VLAN ID.
        should_recover_tags: Whether to recover tags.

    Returns:
        dict: Dictionary containing live mount information
    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        snapshot_fid = self.validate_id(snapshot_fid, "snapshot_fid")

        query_name = "gps_vm_livemount"
        variables = {
            "snapshotFid": snapshot_fid,
            "hostID": host_id,
            "vmName": vm_name,
            "datastoreName": data_store_name

        }
        if disable_network:
            variables['disableNetwork'] = self.to_boolean(disable_network)

        if remove_network_devices:
            variables['removeNetworkDevices'] = self.to_boolean(remove_network_devices)

        if power_on:
            variables['powerOn'] = self.to_boolean(power_on)

        if keep_mac_addresses:
            variables['keepMacAddresses'] = self.to_boolean(keep_mac_addresses)

        if create_data_store_only:
            variables['createDatastoreOnly'] = self.to_boolean(create_data_store_only)

        if should_recover_tags:
            variables['shouldRecoverTags'] = self.to_boolean(should_recover_tags)

        if vlan:
            variables['vlan'] = int(vlan)

        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def create_vm_snapshot(self, snapshot_id: str, sla_id: str = None):
    """
    Create snapshot of a system.
    Args:
        snapshot_id: The Snapshot ID of the snapshot that needs to be created.
        sla_id: The SLA ID of the snapshot that needs to be created.

     Returns:
        dict: Dictionary containing snapshot information.
    Raises:
        RequestException: If the query to Polaris returned an error

    """

    try:
        variables = {}

        snapshot_id = self.validate_id(snapshot_id, "snapshot_id")
        variables['snappableId'] = snapshot_id

        if sla_id:
            variables['slaID'] = sla_id.strip()

        return self._query_raw(query_name="gps_vm_snapshot_create", variables=variables)
    except Exception:
        raise


def list_vsphere_hosts(self, first: int, after: str = None, filters: list = None, sort_by: enumerate = None,
                       sort_order: enumerate = None):
    """
    Retrieves a list of available Vsphere hosts.
    Args:
        after: The next page cursor to retrieve the next set of results.
        first : Number of results to retrieve in the response.
        filters: Filters the SLA result. Supported fields of class GlobalSlaQueryFilterInputField.
        sort_by: Sorts the result using HierarchySortByField.
        sort_order: Sorting orders ASC or DESC.

    Returns:
        dict: Dictionary containing list of Vsphere hosts.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error.

    """
    try:
        variables = {}

        if not first:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("first"))
        first = self.check_first_arg(first)
        variables['first'] = first

        if isinstance(filters, str):
            filters = [filters]

        if filters:
            variables['filter'] = filters

        if after:
            variables['after'] = after.strip()

        if sort_by:
            supported_sla_sort_by = self.get_enum_values(name="HierarchySortByField")
            if sort_by not in supported_sla_sort_by:
                raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_by, 'sort_by', supported_sla_sort_by))

            variables['sortBy'] = sort_by

        if sort_order:
            supported_sla_sort_order = self.get_enum_values(name="HierarchySortOrder")
            if sort_order not in supported_sla_sort_order:
                raise ValueError(
                    ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_order, 'sort_order', supported_sla_sort_order))

            variables['sortOrder'] = sort_order

        return self._query_raw(query_name="gps_vm_hosts", variables=variables)
    except Exception:
        raise


def export_vm_snapshot(self, config: dict, id_: str):
    """
    Export a snapshot of a virtual machine.
    Args:

        id_: The object ID.
        config: Configuration parameters for exporting snapshot.

    Returns:
        dict: Dictionary containing snapshot information.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error

    """

    try:
        variables = {}

        id_ = self.validate_id(id_, "id_")
        variables['id'] = id_

        if not config:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("config"))

        if not isinstance(config, dict):
            raise ValueError(ERROR_MESSAGES['INVALID_CONFIG'].format(config))

        data_store_id = config.get('datastoreId', '')
        host_id = config.get('hostId', '')
        cluster_id = config.get('clusterId', '')
        snapshot_id = config.get("requiredRecoveryParameters", {}).get("snapshotId", '')

        if not data_store_id or (not host_id and not cluster_id) or not snapshot_id:
            raise ValueError(ERROR_MESSAGES['REQUIRED_KEYS_IN_CONFIG'])

        variables['config'] = config

        return self._query_raw(query_name="gps_vm_export", variables=variables)
    except Exception:
        raise


def list_vsphere_datastores(self, host_id: str, first: int = None, after: str = None, filters: list = None,
                            sort_by: enumerate = None, sort_order: enumerate = None):
    """
    Retrieves a list of datastores on a Vsphere host.
    Args:
        host_id:  The Host ID.
        after: The next page cursor to retrieve the next set of results.
        first : Number of results to retrieve in the response.
        filters: Filters the SLA result. Supported fields of class GlobalSlaQueryFilterInputField.
        sort_by: Sorts the result using HierarchySortByField.
        sort_order: Sorting orders ASC or DESC.

    Returns:
        dict: Dictionary containing list of Vsphere datastores.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error.

    """
    try:
        variables = {}

        host_id = self.validate_id(host_id, "host_id")
        variables['hostId'] = host_id

        first = self.check_first_arg(first)
        if first:
            variables['first'] = first

        if isinstance(filters, str):
            filters = [filters]

        if filters:
            variables['filter'] = filters

        if after:
            variables['after'] = after.strip()

        if sort_by:
            supported_sla_sort_by = self.get_enum_values(name="HierarchySortByField")
            if sort_by not in supported_sla_sort_by:
                raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_by, 'sort_by', supported_sla_sort_by))

            variables['sortBy'] = sort_by

        if sort_order:
            supported_sla_sort_order = self.get_enum_values(name="HierarchySortOrder")
            if sort_order not in supported_sla_sort_order:
                raise ValueError(
                    ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(sort_order, 'sort_order', supported_sla_sort_order))

            variables['sortOrder'] = sort_order

        return self._query_raw(query_name="gps_vm_datastores", variables=variables)
    except Exception:
        raise


def get_async_request_result(self, request_id: str, cluster_id: str):
    """
    Retrieves the result of an asynchronous request. These requests can be triggered by calling functions such as
    export_vm_snapshot, create_vm_livemount, request_download_snapshot_files or create_vm_snapshot.
    Args:
        request_id: The ID of the asynchronous request.
        cluster_id: The ID of the cluster where the request was made.

    Returns:
        dict: Dictionary containing the result of the request.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error.

    """
    try:
        query_name = "gps_async_request_result"
        variables = {}

        if not request_id:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("request_id"))
        variables['id'] = request_id

        if not cluster_id:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("cluster_id"))
        variables['clusterUuid'] = cluster_id

        return self._query_raw(query_name=query_name, variables=variables)
    except Exception:
        raise


def recover_files(self, snapshot_id: str, cluster_id: str, restore_config: Union[dict, list],
                  destination_object_id: str = None, should_use_agent: bool = False, should_restore_x_attrs: bool = False,
                  ignore_errors: bool = False):
    """
    Recover files from a snapshot back into a system.
    Args:
        snapshot_id: ID of the snapshot from which to recover files.
        cluster_id: ID of the cluster where the snapshot resides.
        restore_config: List or dict of type RestorePathPairInput.
        destination_object_id: ID of the object where the files will be restored into. If not provided, Rubrik will use
         the snapshots object.
        should_use_agent: Whether to use an agent.
        should_restore_x_attrs: Whether to preserve custom attributes of the machine.
        ignore_errors: Whether to ignore errors.

    Returns:
        dict: Dictionary containing recovery request ID.
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "gps_vm_files_recover"
        variables = {"id": self.validate_id(snapshot_id, "snapshot_id"),
                     "clusterUuid": self.validate_id(cluster_id, "cluster_id")}
        config = {}

        if destination_object_id:
            config["destObjectId"] = destination_object_id

        if should_use_agent:
            config["shouldUseAgent"] = self.to_boolean(should_use_agent)

        if should_restore_x_attrs:
            config["shouldRestoreXAttrs"] = self.to_boolean(should_restore_x_attrs)

        if ignore_errors:
            config["ignoreErrors"] = self.to_boolean(ignore_errors)

        if not restore_config:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('restore_config'))

        if isinstance(restore_config, dict):
            restore_config = [restore_config]

        config["restoreConfig"] = [{"restorePathPair": path_pair} for path_pair in restore_config]
        variables["config"] = config

        return self._query_raw(query_name=query_name, variables=variables)
    except Exception:
        raise

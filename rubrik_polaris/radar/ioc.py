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

from typing import Union, List

"""
Collection of methods related to IOC scans.
"""

ERROR_MESSAGES = {
    'MISSING_PARAMETERS_IN_SCAN_RESULT': 'scan_id and cluster_id fields are required.',
    'INVALID_FIELD_TYPE': "'{}' is an invalid value for '{}'. Value must be in {}.",
    'REQUIRED_ARGUMENT': '{} field is required.'
}


def trigger_ioc_scan(self, object_ids: Union[str, List[str]], cluster_id: str,
                     indicators_of_compromise: Union[dict, list], scan_name: str = None,
                     max_matches_per_snapshot: int = None,
                     snapshot_scan_limit: dict = None,
                     maximum_file_size_to_scan: int = None, minimum_file_size_to_scan: int = None,
                     path_to_include: Union[str, List[str]] = None, path_to_exclude: Union[str, List[str]] = None,
                     path_to_exempt: Union[str, List[str]] = None, requested_hash_types: Union[str, List[str]] = None):
    """Triggers an Radar IOC scan on multiple systems for specified IOC's in a cluster.

   Args:
       object_ids (str|list): ID/ID's of objects to scan.
       cluster_id (str): Cluster ID on which to run the IOC scan.
       indicators_of_compromise (dict|list): Indicators to scan for. Provide a single object or list of
                                             objects of type `IndicatorOfCompromiseInput`.
       scan_name (str): Name of the scan to trigger.
       max_matches_per_snapshot (int): Maximum number of matches per snapshot, per IOC.
                                        Scanning for an IOC within a snapshot
                                        will terminate once this many matches have been detected.
       snapshot_scan_limit (dict): Limit which snapshots to include in the malware scan.
                                   Provide input object of type `MalwareScanSnapshotLimitInput`
       maximum_file_size_to_scan (int): Maximum size of file in bytes that will be included in scan.
       minimum_file_size_to_scan (int): Minimum size of file in bytes that will be included in scan.
       path_to_include (str|list): Paths that will be included in the scan.
       path_to_exclude (str|list): Paths that will be excluded from the scan.
       path_to_exempt (str|list): Paths that will be exempted from exclusion in the scan.
       requested_hash_types (str|list): `HashTypeEnum` type enum value.

   Returns:
       dict: Dictionary containing the scan results

   Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error

   """
    try:
        query_name = "radar_ioc_scan"
        variables = {
            "input": {}
        }

        if cluster_id:
            variables["input"]["clusterUuid"] = cluster_id
        else:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('cluster_id'))

        malware_scan_config = {}
        if object_ids:
            malware_scan_config["objectIds"] = object_ids if isinstance(object_ids, list) else [object_ids]
        else:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('object_ids'))

        if indicators_of_compromise:
            malware_scan_config["indicatorsOfCompromise"] = indicators_of_compromise if isinstance(
                indicators_of_compromise, list) else [indicators_of_compromise]
        else:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('indicators_of_compromise'))

        if scan_name:
            malware_scan_config["name"] = scan_name

        if snapshot_scan_limit:
            malware_scan_config["snapshotScanLimit"] = snapshot_scan_limit

        if max_matches_per_snapshot is not None:
            malware_scan_config["maxMatchesPerSnapshot"] = max_matches_per_snapshot

        path_filter = {}
        if path_to_include:
            path_filter["includes"] = path_to_include if isinstance(path_to_include, list) else [path_to_include]
        if path_to_exclude:
            path_filter["excludes"] = path_to_exclude if isinstance(path_to_exclude, list) else [path_to_exclude]
        if path_to_exempt:
            path_filter["exceptions"] = path_to_exempt if isinstance(path_to_exempt, list) else [path_to_exempt]

        file_size_limits = {}
        if maximum_file_size_to_scan:
            file_size_limits["maximumSizeInBytes"] = maximum_file_size_to_scan
        if minimum_file_size_to_scan:
            file_size_limits["minimumSizeInBytes"] = minimum_file_size_to_scan

        file_scan_criteria = {}
        if path_filter:
            file_scan_criteria["pathFilter"] = path_filter
        if file_size_limits:
            file_scan_criteria["fileSizeLimits"] = file_size_limits

        if file_scan_criteria:
            malware_scan_config["fileScanCriteria"] = file_scan_criteria

        if requested_hash_types:
            if not isinstance(requested_hash_types, list):
                requested_hash_types = [requested_hash_types]
            supported_hash_types = self.get_enum_values(name="HashTypeEnum")
            if not set(requested_hash_types).issubset(supported_hash_types):
                raise ValueError(
                    ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(requested_hash_types, 'requested_hash_types', 
                                                                supported_hash_types))
            malware_scan_config["requestedMatchDetails"] = {
                "requestedHashTypes": requested_hash_types
            }

        variables["input"]["malwareScanConfig"] = malware_scan_config
        
        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def get_ioc_scan_list(self, cluster_id):
    """Get the list of Radar IOC scans on a cluster.

    Args:
        cluster_id (str): Cluster ID whose IOC scans are to be listed.

    Returns:
        dict: Dictionary containing the list of IOC scans

    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error

    """
    try:
        if not cluster_id:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("cluster_id"))
        query_name = "radar_ioc_scan_list"
        variables = {
            "input": {
                "clusterUuid": cluster_id,
            }
        }

        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def get_ioc_scan_result(self, scan_id: str, cluster_id: str):
    """Retrieve the results of a Radar IOC scan.

    Args:
        scan_id (str): IOC scan ID.
        cluster_id (str): Cluster ID on which IOC scan was ran.

    Returns:
        dict: Dictionary containing the scan results

    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error

    """
    try:
        if not scan_id or not cluster_id:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_RESULT'])
        query_name = "radar_ioc_scan_result"
        variables = {
            "input": {
                "id": scan_id,
                "clusterUuid": cluster_id,
            }
        }

        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise

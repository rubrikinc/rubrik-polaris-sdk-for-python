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
Collection of methods that interact with Polaris primitives.
"""


def get_sla_domains(self, sla_domain_name=""):
    """Retrieves dictionary of SLA Domain Names and Identifiers.

    Args:
        sla_domain_name (str): Rubrik SLA Domain name

    Returns:
        dict: The complete set of SLA domains or a one element dict if a non-empty `sla_domain_name` is given and found.

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> client = PolarisClient()
        >>> sla_domains = client.get_sla_domains()
    """
    from rubrik_polaris.exceptions import RequestException

    try:
        query_name = "core_sla_list"
        variables = {
            "filter": {
                "field": "NAME",
                "text": sla_domain_name
            }
        }
        response = self._query(query_name, variables)
        if sla_domain_name:
            for node in response:
                if node['name'] == sla_domain_name:
                    return node
        return response
    except Exception:
        raise


def submit_on_demand(self, object_ids, sla_id, wait=False):
    """Submits On Demand Snapshot request for the given set of object id's and assign the given SLA to the snapshots.

    Args:
        object_ids (list): List of Rubrik Object IDs
        sla_id (str): Rubrik SLA Domain ID
        wait (bool): Threaded wait for all processes to complete

    Returns:
        list: List of errors if any occurred

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> object_ids = client.get_object_ids_gce(region='us-west-1')
        >>> sla_domain_id = client.get_sla_domains('Gold')[0]['id']
        >>> client.submit_on_demand(object_ids, sla_domain_id, wait=True)
    """
    from rubrik_polaris.exceptions import RequestException
    try:
        mutation_name = "core_snappable_on_demand"
        variables = {
            "objectIds": object_ids,
            "slaId": sla_id
        }
        response = self._query(mutation_name, variables)

        results = []

        if response['errors']:
            for error_object in response['errors']:
                results.append(error_object)

        if wait:
            results = self._monitor_task(response['taskchainUuids'])

        # TODO: find a better way to report errors per uuid

        return results
    except Exception:
        raise


def submit_assign_sla(self, object_ids=[], sla_id=None, apply_to_existing_snapshots=None, existing_snapshot_retention=None, global_sla_assign_type="protectWithSlaId"):
    """Submits a Rubrik SLA change for objects

    Args:
        object_ids (list): List of Rubrik Object IDs
        global_sla_assign_type (str): Define assignment type noAssignment/doNotProtect/protectWithSlaId
        sla_id (str): Rubrik SLA Domain ID
        apply_to_existing_snapshots (bool): Apply retention policy to pre-existing snapshots
        existing_snapshot_retention (str): Snapshot handling on doNotProtect RETAIN_SNAPSHOTS/KEEP_FOREVER/EXPIRE_IMMEDIATELY
        global_sla_assign_type (str): ...
    
    Returns:
        list: List of objects assigned the SLA

    Raises:
        RequestException: If the query to Polaris returned an error
    
    Examples:
        >>> object_ids = client.get_object_ids_gce(region='us-west-1')
        >>> sla_domain_id = client.get_sla_domains('Gold')[0]['id']
        >>> client.submit_assign_sla(object_ids, sla_domain_id)
    """
    from rubrik_polaris.exceptions import RequestException

    try:
        mutation_name = "core_sla_assign"
        variables = {
            "shouldApplyToExistingSnapshots": apply_to_existing_snapshots,
            "existingSnapshotRetention": existing_snapshot_retention,
            "globalSlaAssignType": global_sla_assign_type,
            "objectIds": object_ids,
            "slaId": sla_id
        }
        response = self._query(mutation_name, variables)
        return response
    except Exception:
        raise


def get_task_status(self, task_chain_id):
    """Retrieve task status from Polaris

    Args:
        task_chain_id (str): Task Chain UUID from request

    Returns:
        str: Task state

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    from rubrik_polaris.exceptions import RequestException

    try:
        query_name = "core_taskchain_status"
        variables = {
            "filter": task_chain_id
        }
        response = self._query(query_name, variables)
        return response['taskchain']['state']
    except Exception:
        raise


def _get_snapshot(self, snapshot_id=None):
    try:
        query_name = "core_snappable_snapshot"
        variables = {
            "snapshot_id": snapshot_id
        }
        response = self._query(query_name, variables)
        if len(response) == 0:
            return {}
        return response
    except Exception:
        raise


def get_snapshots(self, snappable_id=None, recovery_point=None):
    """Retrieve Snapshots for a Snappable from Polaris

    Args:
        snappable_id (str): Object UUID
        recovery_point (str): Optional datetime of snapshot to return, or 'latest', or not defined to return all
        
    Returns:
        dict: A dictionary of snapshots or a single snapshot if 'latest' was passed as `recovery_point`. If no snapshots are found, an empty dict is returned.

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> snappables = client.get_object_ids_ec2(tags={"Environment": "staging"})
        >>> for snappable in snappables:
        ...    snapshot = client.get_snapshots(snappable, recovery_point='latest')
        ...    if snapshot:
        ...        print(snapshot[0])
    """
    from dateutil.parser import parse
    from dateutil.tz import tzlocal

    try:
        query_name = "core_snappable_snapshots"
        variables = {
            "snappable_id": snappable_id
        }
        if recovery_point == 'latest':
            variables['first'] = 1

        response = self._query(query_name, variables)

        if len(response) == 0:
            return {}

        snapshot_comparison = {}
        for snapshot in response:
            if recovery_point != 'latest':
                parsed_snapshot_date = parse(snapshot['date']).astimezone()
                parsed_recovery_point = parse(recovery_point)
                parsed_recovery_point = parsed_recovery_point.replace(tzinfo=tzlocal())
                snapshot['date_local'] = parsed_snapshot_date.isoformat()
                if parsed_snapshot_date >= parsed_recovery_point:
                    snapshot_comparison[abs(parsed_recovery_point - parsed_snapshot_date)] = snapshot

        if recovery_point != 'latest':
            return snapshot_comparison[min(snapshot_comparison)][0]
        return response[0]
    except Exception:
        raise


def get_event_series_list(self, object_type=[], status=[], activity_type=[], severity=[], cluster_ids=[], start_time=None, end_time = None):
    """Retrieve Events from Polaris

    Args:
        object_type (list): List of Object Types
        status (list): List of Event Status
        activity_type (list): List of Activity Types
        severity (list): List of severities
        cluster_ids (list): List of Cluster IDs (UUID)
        start_date (datetime): Timestamp to start return set from
        end_date (datetime): Timestamp to end return set from

    Returns:
        list: A list of dictionaries of Event Data

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "core_event_series_list"
        variables = {
            "filters": {
                "objectType": object_type,
                "lastActivityStatus": status,
                "lastActivityType": activity_type,
                "severity": severity,
                "cluster": {
                    "id": cluster_ids,
                },
                "lastUpdated_gt": start_time,
                "lastUpdated_lt": end_time,
                "objectName": ""
            }
        }
        response = self._query(query_name, variables)
        return response
    except Exception:
        raise


def get_report_data(self, object_type=[], cluster_ids=[]):
    """Retrieve Report Data from Polaris

    Args:
        object_type (list): List of object type
        cluster_ids (list): List of cluster id's

    Returns:
        list: A list of dictionaries of Report data

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "core_report_data"
        variables = {
            "first": 1000,
            "filters": {
                "objectType": object_type,
                "complianceStatus": [],
                "protectionStatus": [],
                "cluster": {
                    "id": cluster_ids,
                },
            },
        }
        response = self._query(query_name, variables)
        return response
    except Exception:
        raise

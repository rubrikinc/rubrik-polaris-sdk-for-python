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
Collection of methods for sonar sensitive hits.
"""
from datetime import date, timedelta

ERROR_MESSAGES = {
    'REQUIRED_ARGUMENT': '{} field is required.',
    'MISSING_PARAMETERS': 'snapshot_id and snappable_id(object ID) fields are required.'
}


def get_sensitive_hits_object_list(self, day: str, timezone: str):
    """
    To get the sonar sensitive hits object list.

    Args:
        day (str): Specify the date.
        timezone (str): Specify timezone.

    Returns:
        dict: Dictionary containing list of sonar sensitive hits object.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:

        if not day:
            raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('day'))

        variables = {
            'day': day,
            'timezone': timezone
        }

        response = self._query_raw(query_name="sonar_sensitive_hits_object_list", variables=variables)
        return response

    except Exception:
        raise


def get_sensitive_hits_object_detail(self, snapshot_id: str, snappable_id: str):
    """
    To get the sonar sensitive hits object details.

    Args:
        snapshot_id (str): Snapshot ID to get results.
        snappable_id (str): Snappable(Object) ID to get results.

    Returns:
        dict: Dictionary containing details of sonar sensitive hits object.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:

        if not snapshot_id or not snappable_id:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS'])

        variables = {
            "snapshotFid": snapshot_id,
            "snappableFid": snappable_id
        }
        response = self._query_raw(query_name="sonar_sensitive_hits_object_detail", variables=variables)
        return response

    except Exception:
        raise


def get_sensitive_hits(self, search_time_period: int = 7, object_name=None):
    """
    To get the sonar sensitive hits.

    Args:
        search_time_period (int): The number of days in the past to look for sensitive hits.
        object_name (str): The object_name to filter objects.
    Returns:
        dict: Dictionary containing list of sonar sensitive hits.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:
        search_time_period = self.to_number(search_time_period)
        search_day = date.today()
        object_details = {}

        sonar_object_detail = self.get_sensitive_hits_object_list(day=search_day.strftime("%Y-%m-%d"), timezone="UTC")
        for sonar_object in sonar_object_detail["data"]["policyObjConnection"]["edges"]:
            if object_name:
                if sonar_object["node"]["snappable"]["name"] == object_name:
                    object_details["snappable_id"] = sonar_object["node"]["snappable"]["id"]
                    object_details["snapshot_fid"] = sonar_object["node"]["objectStatus"]["latestSnapshotResult"][
                        "snapshotFid"]
            else:
                object_details["snappable_id"] = sonar_object["node"]["snappable"]["id"]
                object_details["snapshot_fid"] = sonar_object["node"]["objectStatus"]["latestSnapshotResult"][
                    "snapshotFid"]

        if len(object_details) == 0:
            for d in range(1, search_time_period):
                past_search_day = search_day - timedelta(days=d)

                sonar_object_detail = self.get_sensitive_hits_object_list(day=past_search_day.strftime("%Y-%m-%d"),
                                                                          timezone="UTC")
                for sonar_object in sonar_object_detail["data"]["policyObjConnection"]["edges"]:
                    if object_name:
                        if sonar_object["node"]["snappable"]["name"] == object_name:
                            object_details["snappable_id"] = sonar_object["node"]["snappable"]["id"]
                            object_details["snapshot_fid"] = sonar_object["node"]["objectStatus"]["latestSnapshotResult"][
                                "snapshotFid"]
                    else:
                        object_details["snappable_id"] = sonar_object["node"]["snappable"]["id"]
                        object_details["snapshot_fid"] = sonar_object["node"]["objectStatus"]["latestSnapshotResult"][
                            "snapshotFid"]

                if len(object_details) == 1:
                    break

        if len(object_details) == 0:
            return {}

        sensitive_hits = self.get_sensitive_hits_object_detail(snapshot_id=object_details["snapshot_fid"],
                                                               snappable_id=object_details["snappable_id"])
        return sensitive_hits

    except Exception:
        raise

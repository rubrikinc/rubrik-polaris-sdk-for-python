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
Collection of methods to obtain csv results.
"""

ERROR_MESSAGES = {
    'MISSING_PARAMETERS_IN_CSV_RESULT': 'cluster_id, snapshot_id and snappable_id(object ID) fields are required.'
}


def get_csv_result(self, cluster_id, snapshot_id, snappable_id):
    """Retrieve the download link for the Radar CSV analyzed file .

    Args:
        cluster_id (str): Cluster ID for analysis.
        snapshot_id (str): Snapshot ID for analysis.
        snappable_id (str): Snappable(Object) ID for analysis.

    Returns:
        dict: Dictionary containing download link

    Raises:
        RequestException: If the query to Polaris returned an error

    """
    try:
        if not cluster_id or not snapshot_id or not snappable_id:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_CSV_RESULT'])
        query_name = "radar_anomaly_csv_analysis"
        variables = {"clusterUuid": cluster_id,
                     "snapshotId": snapshot_id,
                     "snappableIdNotFid": snappable_id
                     }

        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise

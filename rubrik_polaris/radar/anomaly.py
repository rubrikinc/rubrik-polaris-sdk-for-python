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
Collection of methods for analysis.
"""


def get_analysis_status(self, activity_series_id, cluster_id):
    """Retrieve the analysis status result.

    Args:
        activity_series_id: The ID of the Polaris Event Series.
        cluster_id: Cluster UUID for analysis.

    Returns:
        dict: Dictionary containing download link

    Raises:
        RequestException: If the query to Polaris returned an error

    """
    try:
        variables = {
            'activitySeriesId': self.validate_id(activity_series_id, "activity_series_id"),
            'clusterUuid': self.validate_id(cluster_id, "cluster_id")
        }

        response = self._named_raw_query(query_name="radar_analysis_status", variables=variables)
        return response

    except Exception:
        raise

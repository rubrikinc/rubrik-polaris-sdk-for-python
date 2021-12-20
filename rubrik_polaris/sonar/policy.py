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
Collection of methods for sonar policies
"""


def list_policy_analyzer_groups(self):
    """Retrieve the list of sonar policy analyzer groups.

    Returns:
        dict: Dictionary of sonar policy analyzer groups.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:
        query_name = "sonar_policy_analyzer_groups"
        response = self._query_raw(query_name=query_name)
        return response

    except Exception:
        raise


def list_policies(self):
    """Retrieves available sonar policies

    Returns:
        dict: Details of policies

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "sonar_policies"
        return self._query_raw(query_name=query_name)
    except Exception:
        raise

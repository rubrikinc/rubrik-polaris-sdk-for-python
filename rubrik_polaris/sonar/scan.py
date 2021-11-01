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
Collection of methods for sonar on demand scan
"""

ERROR_MESSAGES = {
    'MISSING_PARAMETERS_IN_SCAN': 'scan_name, resources, and analyzer_groups fields are required.',
    'MISSING_PARAMETERS_IN_SCAN_STATUS': 'crawl_id field is required.',
    'MISSING_PARAMETERS_IN_SCAN_RESULT': 'crawl_id and filters fields are required.',
    "INVALID_FILE_TYPE": "'{}' is an invalid value for 'file type'. Value must be in {}."
}


def trigger_on_demand_scan(self, scan_name, resources, analyzer_groups):
    """
    Trigger an on-demand scan of a system (specifying policies to search for).

    Args:
        scan_name (str): Name of the scan.
        analyzer_groups (list): List of sonar policy analyzer groups.
        resources (list): List of object IDs to scan.
    Returns:
        dict: Response from the API.
    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        if not scan_name or not resources or not analyzer_groups:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN'])
        query_name = "sonar_on_demand_scan"
        variables = {
            "crawlName": scan_name,
            "resources": resources,
            "analyzerGroups": analyzer_groups
        }
        query = self._query_raw(query_name=query_name, variables=variables)

        return query

    except Exception:
        raise


def get_on_demand_scan_status(self, crawl_id):
    """Retrieve the list of scan status details.

    Args:
        crawl_id (str): ID for which scan status is to be obtained.

    Returns:
        dict: Dictionary of list of scan status details.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:
        if not crawl_id:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_STATUS'])
        query_name = "sonar_on_demand_scan_status"
        variables = {
            "crawlId": crawl_id
        }
        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def get_on_demand_scan_result(self, crawl_id, filters):
    """
    Retrieve the download link for the requested scanned file.

    Args:
        crawl_id (str): ID for which file needs to be downloaded.
        filters (dict): Dictionary of filter containing file type.

    Returns:
        dict: Dictionary containing download link for the result file.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:
        if not crawl_id or not filters:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_RESULT'])

        file_type = filters.get('fileType')
        file_type_enum = self.get_enum_values(name="FileCountTypeEnum")
        if file_type not in file_type_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FILE_TYPE'].format(file_type, file_type_enum))

        query_name = "sonar_on_demand_scan_result"
        variables = {
            "crawlId": crawl_id,
            "filter": filters
        }
        query = self._query_raw(query_name=query_name, variables=variables)

        return query

    except Exception:
        raise

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
Collection of methods for sonar csv files.
"""

ERROR_MESSAGES = {
    'MISSING_PARAMETERS_IN_CSV_DOWNLOAD': 'snapshot_id and snappable_id(object ID) fields are required.',
    'INVALID_FIELD_TYPE': "'{}' is an invalid value for '{}'. Value must be in {}.",
}


def get_csv_download(self, snapshot_id, snappable_id, filters=None):
    """Request to download the Sonar CSV Snapshot results file.

    Args:
        snapshot_id (str): Snapshot ID to get results.
        snappable_id (str): Snappable (Object) ID to get results.
        filters (dict): Filters to download csv file.

    Returns:
        dict: Dictionary containing status of sonar csv snapshot results file download .

    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error.
    """
    try:
        query_name = "sonar_csv_download"
        if not snapshot_id or not snappable_id:
            raise ValueError(ERROR_MESSAGES['MISSING_PARAMETERS_IN_CSV_DOWNLOAD'])
        if filters:
            if filters.get("fileType"):
                file_type = filters.get("fileType")
                file_type_enum = self.get_enum_values(name="FileCountTypeEnum")
                if file_type not in file_type_enum:
                    raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(file_type, "file type", file_type_enum))

        variables = {
            "filters": filters,
            "snapshotFid": snapshot_id,
            "snappableFid": snappable_id
        }
        response = self._named_raw_query(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def get_csv_result_download(self, download_id: int):
    """
    To retrieve the Sonar CSV results file download link.

    Args:
        download_id (int): ID of CSV results file to be download.

    Returns:
        dict: Dictionary containing download link of Sonar CSV results file.

    Raises:
        RequestException: If the query to Polaris returned an error.
    """
    try:
        query_name = "sonar_csv_result_download"

        download_id = self.validate_id(download_id, "download_id")
        variables = {
            "downloadId": download_id
        }
        response = self._named_raw_query(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise

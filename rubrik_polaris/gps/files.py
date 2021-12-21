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
Collection of methods for gps files.
"""

ERROR_MESSAGES = {
    'MISSING_PATHS_PARAMETER_IN_FILES': 'paths field is required.',
}


def get_snapshot_files(self, snapshot_id: str, first: int = None, path: str = None, after: str = None,
                       search_prefix: str = None):
    """Retrieve the list of the available files that can be downloaded.

    Args:
        first (int): Number of results to retrieve in the response.
        after (str): The next page cursor to retrieve the next set of results.
        path (str): The path of the folder to list the sub-files.
                    If not provided the root directory files will be returned.
        search_prefix (str): Provide a keyword to search in the file names.
        snapshot_id (str): The Snapshot ID of the file that needs to be downloaded.

    Returns:
        dict: Dictionary containing list of files

    Raises:
        RequestException: If the query to Polaris returned an error

    """
    try:
        snapshot_id = self.validate_id(snapshot_id, "snapshot_id")

        query_name = "gps_snapshot_files"
        variables = {
            "snapshotFid": snapshot_id,
            "path": "" if not path else path
        }

        first = self.check_first_arg(first)
        if first:
            variables['first'] = first
        if after:
            variables['after'] = after
        if search_prefix:
            variables['searchPrefix'] = search_prefix

        response = self._query_raw(query_name=query_name, variables=variables)
        return response

    except Exception:
        raise


def request_download_snapshot_files(self, snapshot_id: str, paths: list, delta_type_filter: enumerate = None,
                                    next_snapshot_fid: str = None):
    """

    Args:
        snapshot_id (str): The Snapshot ID of the file that needs to be downloaded.
        paths (array): List of paths to download.
        delta_type_filter (enumerate): DeltaTypeEnum filter
        next_snapshot_fid (str): The next Snapshot FID.

    Returns:
        dict: Dictionary containing list of files
    Raises:
        ValueError: If input is invalid
        RequestException: If the query to Polaris returned an error
    """

    try:
        snapshot_id = self.validate_id(snapshot_id, "snapshot_id")

        if isinstance(paths, str):
            paths = paths.strip()
            if not paths:
                raise ValueError(ERROR_MESSAGES['MISSING_PATHS_PARAMETER_IN_FILES'])
            paths = [paths]

        variables = {
            "snapshotFid": snapshot_id,
            "paths": paths,
            "deltaTypeFilter": delta_type_filter,
            "nextSnapshotFid": next_snapshot_fid
        }

        return self._query_raw(query_name="gps_file_download", variables=variables)
    except Exception:
        raise

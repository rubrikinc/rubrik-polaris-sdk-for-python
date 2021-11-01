import os

import pytest

from conftest import util_load_json, BASE_URL
from rubrik_polaris.common import util
from rubrik_polaris.gps.files import ERROR_MESSAGES


@pytest.mark.parametrize("snapshot_id, first, path, after, search_prefix, err_msg", [
    ("", 10, "", "", "", util.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("snapshot_id")),
    ("dummy_id", "abc", "", "", "", util.ERROR_MESSAGES['INVALID_NUMBER'].format("abc")),
    ("dummy_id", -1, "", "", "", util.ERROR_MESSAGES['INVALID_FIRST'].format(-1))
])
def test_get_snapshot_files_when_invalid_values_are_provided(client, snapshot_id, first, path, after, search_prefix,
                                                             err_msg):
    """
    Tests get_snapshot_files method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.gps.files import get_snapshot_files

    with pytest.raises(ValueError) as e:
        get_snapshot_files(client, snapshot_id=snapshot_id, first=first, path=path, after=after,
                           search_prefix=search_prefix)
    assert str(e.value) == err_msg


def test_get_snapshot_files_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_snapshot_files method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.files import get_snapshot_files

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/get_snapshot_files.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_snapshot_files(
        client, snapshot_id="dummy_id", search_prefix="admin", path="/C:", first=10,
        after="Y3Vyc29yOmludDo5"
    )
    assert response == expected_response


def test_request_snapshot_files_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_snapshot_files method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.files import request_download_snapshot_files

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/gps_request_snapshot_file_download_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = request_download_snapshot_files(
        client, snapshot_id="dummy_id", paths="/C:/bootmgr", delta_type_filter=None, next_snapshot_fid=None
    )
    assert response == expected_response


def test_request_snapshot_files_when_valid_values_are_provided_with_empty_paths(requests_mock, client):
    """
    Tests get_snapshot_files method of PolarisClient when valid values are provided having paths as empty array.
    """
    from rubrik_polaris.gps.files import request_download_snapshot_files

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/gps_request_snapshot_file_download_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = request_download_snapshot_files(
        client, snapshot_id="dummy_id", paths=[], delta_type_filter=None, next_snapshot_fid=None
    )
    assert response == expected_response


@pytest.mark.parametrize("snapshot_id, paths, delta, nxt_snapshot_id, err_msg", [
    (" ", [], "", "", util.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("snapshot_id")),
    ("dummy_id", "", "", "", ERROR_MESSAGES['MISSING_PATHS_PARAMETER_IN_FILES']),
])
def test_request_snapshot_files_when_invalid_values_are_provided(client, snapshot_id, paths, delta, nxt_snapshot_id,
                                                                 err_msg):
    """
    Tests get_snapshot_files method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.gps.files import request_download_snapshot_files

    with pytest.raises(ValueError) as e:
        request_download_snapshot_files(client, snapshot_id=snapshot_id, paths=paths, delta_type_filter=delta,
                                        next_snapshot_fid=nxt_snapshot_id)
    assert str(e.value) == err_msg

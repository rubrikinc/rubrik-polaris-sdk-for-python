import os

import pytest

from conftest import util_load_json, BASE_URL


def test_get_user_downloads_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_user_downloads method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.user import get_user_downloads

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/user_download.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_user_downloads(client)
    assert response == expected_response

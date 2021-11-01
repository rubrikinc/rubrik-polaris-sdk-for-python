import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.common.util import ERROR_MESSAGES


def test_get_sensitive_hits_object_list_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_sensitive_hits_object_list method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.object import get_sensitive_hits_object_list

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/get_sensitive_hits_object_list_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_sensitive_hits_object_list(client, day="2021-08-21", timezone="")
    assert response == expected_response


def test_get_sensitive_hits_object_list_when_invalid_values_are_provided(client):
    """
    Tests get_sensitive_hits_object_list method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.object import get_sensitive_hits_object_list, ERROR_MESSAGES

    with pytest.raises(ValueError) as e:
        get_sensitive_hits_object_list(client, day="", timezone="")

    assert str(e.value) == ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('day')


def test_get_sensitive_hits_object_detail_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_sensitive_hits_object_detail method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.object import get_sensitive_hits_object_detail

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/get_sensitive_hits_object_detail_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_sensitive_hits_object_detail(client, snapshot_id="1b174c2e-f77b-5006-baea-fe37b2ae429f",
                                                snappable_id="ec5d44e6-8be4-5969-85b3-54fa72c4048a")
    assert response == expected_response


@pytest.mark.parametrize("snapshot_id, snappable_id", [
    ("", "abc"),
    ("123", "")
])
def test_get_sensitive_hits_object_detail_when_invalid_values_are_provided(client, snapshot_id, snappable_id):
    """
    Tests get_sensitive_hits_object_detail method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.object import get_sensitive_hits_object_detail, ERROR_MESSAGES

    with pytest.raises(ValueError) as e:
        get_sensitive_hits_object_detail(client, snapshot_id=snapshot_id, snappable_id=snappable_id)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS']


def test_get_sensitive_hits_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_sensitive_hits method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.object import get_sensitive_hits

    expected_response_list = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                         "test_data/get_sensitive_hits_object_list_response.json"))
    expected_response_details = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                            "test_data/get_sensitive_hits_object_detail_response.json"))
    responses = [
        {'json': expected_response_list},
        {'json': expected_response_details}
    ]
    requests_mock.post(BASE_URL + "/graphql", responses)

    response = get_sensitive_hits(client)
    assert response == expected_response_details


@pytest.mark.parametrize("search_time_period, object_name, error", [
    ("dummy", "", ERROR_MESSAGES['INVALID_NUMBER'].format("dummy"))
])
def test_get_sensitive_hits_when_invalid_values_are_provided(client, search_time_period, object_name, error):
    """
    Tests get_sensitive_hits method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.object import get_sensitive_hits

    with pytest.raises(ValueError) as e:
        get_sensitive_hits(client, search_time_period=search_time_period, object_name=object_name)

    assert str(e.value) == error

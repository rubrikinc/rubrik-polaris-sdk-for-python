import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.radar.ioc import ERROR_MESSAGES


@pytest.mark.parametrize("object_ids, cluster_id, indicators_of_compromise, error",
                         [("", "dummy-cluster-id", {"dummmy-type": "dummy-val"},
                           ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("object_ids")),
                          ([], "dummy-cluster-id", {"dummmy-type": "dummy-val"},
                           ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("object_ids")),
                          ("dummy-object-id", "", {"dummmy-type": "dummy-val"},
                           ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("cluster_id")),
                          ("dummy-object-id", "dummy-cluster-id", {},
                           ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("indicators_of_compromise")),
                          ("dummy-object-id", "dummy-cluster-id", [],
                           ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("indicators_of_compromise"))
                          ])
def test_trigger_ioc_scan_when_invalid_values_are_provided(client, object_ids, cluster_id, indicators_of_compromise,
                                                           error):
    """
    Tests trigger_ioc_scan method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.radar.ioc import trigger_ioc_scan

    params = {
        "object_ids": object_ids,
        "cluster_id": cluster_id,
        "indicators_of_compromise": indicators_of_compromise,
    }
    with pytest.raises(ValueError) as e:
        trigger_ioc_scan(client, **params)
    assert str(e.value) == error


def test_trigger_ioc_scan_when_valid_values_are_provided(requests_mock, client):
    """
    Tests trigger_ioc_scan method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.radar.ioc import trigger_ioc_scan

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/trigger_ioc_scan.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = trigger_ioc_scan(client, "dummy-object-id", "dummy-cluster-id", {"dummmy-type": "dummy-val"})
    assert response == expected_response


def test_get_ioc_scan_list_when_invalid_values_are_provided(client):
    """
    Tests get_ioc_scan_list method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.radar.ioc import get_ioc_scan_list

    with pytest.raises(ValueError) as e:
        get_ioc_scan_list(client, cluster_id='')
    assert str(e.value) == ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("cluster_id")


def test_get_ioc_scan_list_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_ioc_scan_list method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.radar.ioc import get_ioc_scan_list

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/radar_ioc_scan_list.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_ioc_scan_list(client, cluster_id="ac0a6844-a2fc-52b0-bb71-6a55f43677be")
    assert response == expected_response


@pytest.mark.parametrize("scan_id, cluster_id", [
    ("", "abc"),
    ("123", "")
])
def test_get_ioc_scan_result_when_invalid_values_are_provided(client, scan_id, cluster_id):
    """
    Tests get_ioc_scan_result method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.radar.ioc import get_ioc_scan_result

    with pytest.raises(ValueError) as e:
        get_ioc_scan_result(client, scan_id=scan_id, cluster_id=cluster_id)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_RESULT']


def test_get_ioc_scan_result_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_ioc_scan_result method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.radar.ioc import get_ioc_scan_result

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/radar_ioc_scan_result.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_ioc_scan_result(client, scan_id="c38ec074-0c45-5c72-b611-3322cbd46776",
                                   cluster_id="ac0a6844-a2fc-52b0-bb71-6a55f43677be")
    assert response == expected_response

import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.sonar.scan import ERROR_MESSAGES

FILE_TYPES = ['ANY', 'HITS', 'STALE', 'OPEN_ACCESS', 'STALE_HITS', 'OPEN_ACCESS_HITS']


@pytest.mark.parametrize("scan_name, resources, analyzer_groups", [
    ("", [{"snappableFid": "dummy_id"}], [{"id": "dummy_id"}]),
    ("scan_name", [], [{"id": "dummy_id"}]),
    ("scan_name", [{"snappableFid": "dummy_id"}], [])
])
def test_trigger_on_demand_scan_when_invalid_values_are_provided(client, scan_name, resources, analyzer_groups):
    """
    Tests trigger_on_demand_scan method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.scan import trigger_on_demand_scan

    with pytest.raises(ValueError) as e:
        trigger_on_demand_scan(client, scan_name=scan_name, resources=resources, analyzer_groups=analyzer_groups)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN']


def test_trigger_on_demand_scan_when_valid_values_are_provided(requests_mock, client):
    """
    Tests trigger_on_demand_scan method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.scan import trigger_on_demand_scan

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/on_demand_scan.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    scan_name = "Scan from SDK"
    resources = [{"snappableFid": "dummy_id"}]
    analyzer_groups = [{"id": "dummy_id", "name": "name", "groupType": "group_type", "analyzers": [{}]}]

    response = trigger_on_demand_scan(
        client, scan_name=scan_name, resources=resources, analyzer_groups=analyzer_groups)
    assert response == expected_response


def test_get_on_demand_scan_status_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_on_demand_scan_status method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.scan import get_on_demand_scan_status

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/on_demand_scan_status.json"))

    requests_mock.post(BASE_URL + "/graphql", json=expected_response)
    response = get_on_demand_scan_status(client, crawl_id="587d147a-add9-4152-b7a0-5a667d99f395")

    assert response == expected_response


@pytest.mark.parametrize("crawl_id", [""])
def test_get_on_demand_scan_status_when_invalid_values_are_provided(client, crawl_id):
    """
    Tests get_on_demand_scan_status method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.scan import get_on_demand_scan_status

    with pytest.raises(ValueError) as e:
        get_on_demand_scan_status(client, crawl_id=crawl_id)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_STATUS']


@pytest.mark.parametrize("crawl_id, filters, err_msg", [
    ("", {"fileType": "HITS"}, ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_RESULT']),
    ("scan_name", {}, ERROR_MESSAGES['MISSING_PARAMETERS_IN_SCAN_RESULT']),
    ("scan_name", {"fileType": "HIT"}, ERROR_MESSAGES['INVALID_FILE_TYPE'].format('HIT', FILE_TYPES))
])
def test_get_on_demand_scan_result_when_invalid_values_are_provided(client, crawl_id, filters, err_msg, requests_mock):
    """
    Tests get_on_demand_scan_result method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.scan import get_on_demand_scan_result

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/file_type_values.json")
    )

    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    with pytest.raises(ValueError) as e:
        get_on_demand_scan_result(client, crawl_id=crawl_id, filters=filters)
    assert str(e.value) == err_msg


def test_get_on_demand_scan_result_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_on_demand_scan_result method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.scan import get_on_demand_scan_result

    query_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                 "test_data/on_demand_scan_result.json"))
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/file_type_values.json")
    )

    responses = [
        {'json': enum_response},
        {'json': query_response}
    ]
    requests_mock.post(BASE_URL + "/graphql", responses)

    response = get_on_demand_scan_result(client, crawl_id="dummy_id", filters={"fileType": "HITS"})
    assert response == query_response

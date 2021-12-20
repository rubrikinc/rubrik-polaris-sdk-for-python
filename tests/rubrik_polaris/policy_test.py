import os
from conftest import util_load_json, BASE_URL


def test_list_policy_analyzer_groups_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_policy_analyzer_groups method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.policy import list_policy_analyzer_groups

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_policy_analyzer_groups.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = list_policy_analyzer_groups(client)
    assert response == expected_response


def test_list_policies_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_policies method of PolarisClient when valid values are provided
    """
    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/list_policies_valid_response.json")
    )
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)
    response = client.list_policies()

    assert response == expected_response

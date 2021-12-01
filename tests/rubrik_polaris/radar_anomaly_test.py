import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.common import validations


def test_get_analysis_status_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_analysis_status method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.radar.anomaly import get_analysis_status

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/get_analysis_status.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_analysis_status(client, activity_series_id="ec9c48ce-5faf-474a-927c-33667355aecd",
                                   cluster_id="cc19573c-db6c-418a-9d48-067a256543ba")
    assert response == expected_response


@pytest.mark.parametrize("activity_series_id, cluster_id, err_msg", [
    ("", "cc19573c-db6c-418a-9d48-067a256543ba", validations.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('activity_series_id')),
    ("cc19573c-db6c-418a-9d48-067a256543ba", "", validations.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format('cluster_id'))
])
def test_get_analysis_status_when_invalid_values_are_provided(client, activity_series_id, cluster_id, err_msg):
    """
    Tests get_analysis_status method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.radar.anomaly import get_analysis_status

    with pytest.raises(ValueError) as e:
        get_analysis_status(client, activity_series_id=activity_series_id, cluster_id=cluster_id)

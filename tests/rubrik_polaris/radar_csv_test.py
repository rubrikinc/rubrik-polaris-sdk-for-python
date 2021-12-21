import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.radar.csv import ERROR_MESSAGES


def test_get_csv_result_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_csv_result method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.radar.csv import get_csv_result

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/get_csv_result.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_csv_result(client, cluster_id="cc19573c-db6c-418a-9d48-067a256543ba",
                              snapshot_id="7b71d588-911c-4165-b6f3-103a1684d2a3",
                              snappable_id="868aa03d-4145-4cb1-808b-e10c4f7a3741-vm-4335")
    assert response == expected_response


@pytest.mark.parametrize("clusterid, snapshotid, snappableid", [
    ("", "", "abc"),
    ("123", "234", "")
])
def test_get_csv_result_when_invalid_values_are_provided(client, clusterid, snapshotid, snappableid):
    """
    Tests get_csv_result method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.radar.csv import get_csv_result

    with pytest.raises(ValueError) as e:
        get_csv_result(client, clusterid, snapshotid, snappableid)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS_IN_CSV_RESULT']

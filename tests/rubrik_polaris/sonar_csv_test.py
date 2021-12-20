import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.sonar.csv import ERROR_MESSAGES
from rubrik_polaris.common import validations


def test_get_csv_download_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_csv_download method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.csv import get_csv_download

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/sonar_csv_download.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_csv_download(client,
                                snapshot_id="c38ec074-0c45-5c72-b611-3322cbd46776",
                                snappable_id="ac0a6844-a2fc-52b0-bb71-6a55f43677be",
                                )
    assert response == expected_response


@pytest.mark.parametrize("snapshot_id, snappable_id", [
    ("", "abc"),
    ("123", "")
])
def test_get_csv_download_when_invalid_values_are_provided(client, snapshot_id, snappable_id):
    """
    Tests get_csv_download method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.csv import get_csv_download

    with pytest.raises(ValueError) as e:
        get_csv_download(client, snapshot_id=snapshot_id, snappable_id=snappable_id)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS_IN_CSV_DOWNLOAD']


def test_get_csv_result_download_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_csv_result_download method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.sonar.csv import get_csv_result_download

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/sonar_csv_result_download.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = get_csv_result_download(client, download_id=107)
    assert response == expected_response


def test_get_csv_result_download_when_invalid_values_are_provided(client):
    """
    Tests get_csv_result_download method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.sonar.csv import get_csv_result_download

    with pytest.raises(ValueError) as e:
        get_csv_result_download(client, download_id="")
    assert str(e.value) == validations.ERROR_MESSAGES['REQUIRED_ARGUMENT'].format("download_id")

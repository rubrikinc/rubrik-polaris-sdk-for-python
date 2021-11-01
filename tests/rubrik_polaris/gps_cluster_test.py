import pytest
import os
from rubrik_polaris.common import util
from rubrik_polaris.gps.cluster import ERROR_MESSAGES
from conftest import util_load_json, BASE_URL


def test_list_clusters_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_clusters method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.gps.cluster import list_clusters

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_clusters.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = list_clusters(client, first=1)
    assert response == expected_response


@pytest.mark.parametrize("first, after, filters, sort_by,sort_order, err_msg", [
    (-10, None, None, None, None, util.ERROR_MESSAGES['INVALID_FIRST'].format(-10)),
    ("x", None, None, None, None, util.ERROR_MESSAGES['INVALID_NUMBER'].format("x")),
    (10, None, None, "Name", None,
     ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("Name", "sort_by", ['RegisteredAt', 'ClusterName', 'ClusterType'])),
    (10, None, None, "ClusterName", "BOTH",
     ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("BOTH", "sort_order", ['Asc', 'Desc']))
])
def test_list_clusters_when_invalid_values_are_provided(client, requests_mock, after, first, filters, sort_by,
                                                        sort_order, err_msg):
    """
    Tests list_clusters of PolarisClient when invalid values are provided.
    """
    from rubrik_polaris.gps.cluster import list_clusters

    enum_sort_by = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/list_clusters_sort_by_values.json")
    )
    enum_sort_order = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/list_clusters_sort_order_values.json")
    )
    responses = [
        {'json': enum_sort_by},
        {'json': enum_sort_order},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_clusters(client, after=after, first=first, filters=filters, sort_by=sort_by, sort_order=sort_order)

    assert str(e.value) == err_msg

import pytest
import os
from rubrik_polaris.common import util
from rubrik_polaris.gps.sla import ERROR_MESSAGES
from conftest import util_load_json, BASE_URL


@pytest.mark.parametrize("after, first, filters, sort_by,sort_order, show_protected_object_count, err_msg", [
    (None, -10, None, None, None, None, util.ERROR_MESSAGES['INVALID_FIRST'].format(-10)),
    (None, "x", None, None, None, None, util.ERROR_MESSAGES['INVALID_NUMBER'].format("x")),
    (None, 10, None, None, None, "t", util.ERROR_MESSAGES['INVALID_BOOLEAN']),
    (None, 10, None, "NAME", "BOTH", "False",
     ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("BOTH", "sort_order", ['ASC', 'DESC']))
])
def test_get_sla_domain_invalid_input(client, requests_mock, after, first, filters, sort_by, sort_order,
                                      show_protected_object_count, err_msg):
    """
    Tests get_sla_domains method of PolarisClient when invalid values are provided.
    """
    from rubrik_polaris.gps.sla import list_sla_domains

    enum_sort_by = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/gps_sla_sort_by_values.json")
    )
    enum_sort_order = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/gps_sla_sort_order_values.json")
    )
    responses = [
        {'json': enum_sort_by},
        {'json': enum_sort_order},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_sla_domains(client, after=after, first=first, filters=filters, sort_by=sort_by, sort_order=sort_order
                        , show_protected_object_count=show_protected_object_count)

    assert str(e.value) == err_msg


def test_get_sla_domain_valid_input(requests_mock, client):
    """
    Tests get_sla_domains method of PolarisClient by passing valid inputs
    """
    from rubrik_polaris.gps.sla import list_sla_domains

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/get_sla_domain_response.json"))
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    response = list_sla_domains(
        client, first=10
    )
    assert response == expected_response

import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.common.core import ERROR_MESSAGES


def test_list_event_series_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_event_series method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.core import list_event_series

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_response.json"))
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_activity_status_values.json"))
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_activity_type_values.json"))
    enum_response3 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_object_type_values.json"))
    enum_response4 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_severity_values.json"))
    enum_response5 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_sort_by_values.json"))
    enum_response6 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_sort_order_values.json"))

    responses = [
        {'json': enum_response},
        {'json': enum_response2},
        {'json': enum_response3},
        {'json': enum_response4},
        {'json': enum_response5},
        {'json': enum_response6},
        {'json': expected_response},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    response = list_event_series(client, activity_status="Success", activity_type="Anomaly", object_type="VmwareVm",
                                 severity="Critical", object_name="sx", first=2, sort_by="LastUpdated", sort_order="Desc",
                                 start_date="2020-10-18", end_date="2021-10-18")
    assert response == expected_response


@pytest.mark.parametrize("first, severity, sort_order, error", [
    (0, None, None, ERROR_MESSAGES["INVALID_FIRST"].format(0)),
    (-1, None, None, ERROR_MESSAGES["INVALID_FIRST"].format(-1)),
    (1, "a", None, ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("a", "severity", ['Critical', 'Warning', 'Info'])),
    (1, None, "a", ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("a", "sort_order", ['Asc', 'Desc']))
])
def test_search_object_when_invalid_values_are_provided(client, first, severity, sort_order, error, requests_mock):
    """
    Tests search_object method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.core import list_event_series
    enum_response1 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_severity_values.json"))
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/event_series_sort_order_values.json"))

    responses = [
        {'json': enum_response1},
        {'json': enum_response2},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_event_series(client, first=first, severity=severity, sort_order=sort_order)
    assert str(e.value) == error


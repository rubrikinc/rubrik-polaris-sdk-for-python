import os
import pytest
from conftest import util_load_json, BASE_URL
from rubrik_polaris.common.object import ERROR_MESSAGES
from rubrik_polaris.common import validations

GROUP_BY_VALUES = ["Month", "Day", "Year", "Week", "Hour", "Quarter"]
OBJECT_ID = "dummy_object_id"


def test_list_vm_objects_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_vm_objects method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.object import list_vm_objects

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_vm_objects.json"))
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json"))
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )

    responses = [
        {'json': enum_response},
        {'json': enum_response2},
        {'json': expected_response},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    response = list_vm_objects(client, first=1, filters=[], sort_order="ASC", sort_by="ID")
    assert response == expected_response


@pytest.mark.parametrize("first, sort_by, sort_order, err_msg", [
    (-10, None, None, ERROR_MESSAGES['INVALID_FIRST'].format(-10)),
    (0, None, None, ERROR_MESSAGES['INVALID_FIRST'].format(0)),
    (1, "NAME", 'a', validations.ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("a", "sort_order", ['ASC', 'DESC']))
])
def test_list_vm_objects_when_invalid_values_are_provided(client, requests_mock, first, sort_by, sort_order, err_msg):
    """
    Tests list_vm_objects method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.object import list_vm_objects
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json")
    )
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )
    responses = [
        {'json': enum_response},
        {'json': enum_response2},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_vm_objects(client, first=first, sort_order=sort_order, sort_by=sort_by)
    assert str(e.value) == err_msg


@pytest.mark.parametrize("field, sort_by, sort_order, err_msg", [
    ("sort_by", 'ID', None, ERROR_MESSAGES['SORT_FIELDS_REQUIRED']),
    ("sort_order", None, 'ASC', ERROR_MESSAGES['SORT_FIELDS_REQUIRED']),
])
def test_list_vm_objects_when_sort_fields_are_required(client, requests_mock, field, sort_by, sort_order, err_msg):
    """
    Tests list_vm_objects method of PolarisClient when invalid sort fields are provided
    """
    from rubrik_polaris.common.object import list_vm_objects
    responses = []
    if field == "sort_by":
        enum_response = util_load_json(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json")
        )
        responses.append({'json': enum_response})
    if field == "sort_order":
        enum_response2 = util_load_json(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
        )
        responses.append({'json': enum_response2})

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_vm_objects(client, sort_order=sort_order, sort_by=sort_by)
    assert str(e.value) == err_msg


def test_search_object_when_valid_values_are_provided(requests_mock, client):
    """
    Tests search_object method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.object import search_object

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/search_object_valid_response.json")
    )
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json"))
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )

    responses = [
        {'json': enum_response},
        {'json': enum_response2},
        {'json': expected_response},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    response = search_object(client, [{"field": "NAME", "texts": ["dev"]}], 2, sort_by="NAME", sort_order="DESC")
    assert response == expected_response


@pytest.mark.parametrize("filters, first, sort_by, sort_order, after, raised, err_message", [
    ([], 0, None, None, None, ValueError, ERROR_MESSAGES["INVALID_FIRST"].format(0)),
    ([], -20, None, None, None, ValueError, ERROR_MESSAGES["INVALID_FIRST"].format(-20)),
    ([], 1, "NAME", 'a', None, ValueError, validations.ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("a", "sort_order",
                                                                                     ['ASC', 'DESC']))
])
def test_search_object_when_invalid_values_are_provided(client, requests_mock, filters, first, sort_by, sort_order,
                                                        after, raised, err_message):
    """
    Tests search_object method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.object import search_object
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json")
    )
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )
    responses = [
        {'json': enum_response},
        {'json': enum_response2},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(raised) as e:
        search_object(client, filters, first, sort_by, sort_order, after)
    assert str(e.value) == err_message


def test_get_object_metadata_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_object_metadata method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.object import get_object_metadata

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/object_metadata.json")
    )

    requests_mock.post(BASE_URL + "/graphql", json=expected_response)
    response = get_object_metadata(client, object_id="86db05d1-292f-5973-b616-2ae3977f4428")

    assert response == expected_response


@pytest.mark.parametrize("object_id", [""])
def test_get_object_metadata_when_invalid_values_are_provided(client, object_id):
    """
    Tests get_object_metadata method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.object import get_object_metadata

    with pytest.raises(ValueError) as e:
        get_object_metadata(client, object_id=object_id)
    assert str(e.value) == ERROR_MESSAGES['MISSING_PARAMETERS_IN_METADATA']


def test_get_object_snapshot_when_valid_values_are_provided(requests_mock, client):
    """
    Tests get_object_snapshot method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.object import get_object_snapshot

    query_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/object_snapshot.json")
    )
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/group_by_values.json")
    )

    responses = [
        {'json': enum_response},
        {'json': enum_response},
        {'json': query_response},
    ]
    requests_mock.post(BASE_URL + "/graphql", responses)

    time_range = {
        "start": "2021-07-31T18:30:00.000Z",
        "end": "2021-08-31T18:29:59.999Z"
    }
    response = get_object_snapshot(client, object_id="86db05d1-292f-5973-b616-2ae3977f4428", snapshot_group_by="Day",
                                   missed_snapshot_group_by="Day", time_range=time_range, timezone_offset=5.5,
                                   cluster_connected=True)

    assert response == query_response
    assert requests_mock.call_count == 4


@pytest.mark.parametrize(
    "object_id, snapshot_group_by, missed_snapshot_group_by, time_range, timezone_offset, cluster_connected, err_msg", [
        (OBJECT_ID, "", "", {}, 0, True, ERROR_MESSAGES['MISSING_PARAMETERS_IN_SNAPSHOT']),
        (OBJECT_ID, "day", "Day", {"start": ""}, 5.5, True, validations.ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
            "day", 'snapshot_group_by', GROUP_BY_VALUES)),
        (OBJECT_ID, "Day", "Second", {"start": ""}, 5.5, True, validations.ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
            "Second", 'missed_snapshot_group_by', GROUP_BY_VALUES)),
        (OBJECT_ID, "Day", "Day", {"start": ""}, "abc", True, ERROR_MESSAGES['INVALID_TIMEZONE_OFFSET'].format("abc")),
        (OBJECT_ID, "Day", "Day", {"start": ""}, 5.5, "True", ERROR_MESSAGES['INVALID_CLUSTER_CONNECTED'].format(
            "True"))
    ])
def test_get_object_snapshot_when_invalid_values_are_provided(client, object_id, snapshot_group_by,
                                                              missed_snapshot_group_by, time_range, timezone_offset,
                                                              cluster_connected, err_msg, requests_mock):
    """
    Tests get_object_snapshot method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.object import get_object_snapshot

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/group_by_values.json")
    )
    requests_mock.post(BASE_URL + "/graphql", json=expected_response)

    with pytest.raises(Exception) as e:
        get_object_snapshot(client, object_id=object_id, snapshot_group_by=snapshot_group_by,
                            missed_snapshot_group_by=missed_snapshot_group_by, time_range=time_range,
                            timezone_offset=timezone_offset, cluster_connected=cluster_connected)

    assert str(e.value) == err_msg


def test_list_objects_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_objects method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.object import list_objects

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_objects.json"))
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json"))
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )
    enum_response3 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/type_filter_values.json"))

    responses = [
        {'json': enum_response},
        {'json': enum_response2},
        {'json': enum_response3},
        {'json': expected_response},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    response = list_objects(client, first=1, sort_by="NAME", sort_order="ASC", type_filter="AzureNativeVm")
    assert response == expected_response


@pytest.mark.parametrize("first, sort_order, err_msg", [
    (0, None, ERROR_MESSAGES['INVALID_FIRST'].format(0)),
    ("a", None, validations.ERROR_MESSAGES['INVALID_NUMBER'].format("a")),
    (1, 'a', validations.ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("a", "sort_order", ['ASC', 'DESC']))
])
def test_list_objects_when_invalid_values_are_provided(client, requests_mock, first, sort_order, err_msg):
    """
    Tests list_objects method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.object import list_objects
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_by_values.json")
    )
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_values.json")
    )
    enum_response3 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/type_filter_values.json"))

    responses = [
        {'json': enum_response},
        {'json': enum_response2},
        {'json': enum_response3}
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_objects(client, first=first, sort_by="ID", sort_order=sort_order)
    assert str(e.value) == err_msg


def test_list_object_snapshots_when_valid_values_are_provided(requests_mock, client):
    """
    Tests list_object_snapshots method of PolarisClient when valid values are provided
    """
    from rubrik_polaris.common.object import list_object_snapshots

    expected_response = util_load_json(os.path.join(os.path.dirname(os.path.realpath(__file__)),
                                                    "test_data/list_object_snapshots.json"))
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/snapshot_sort_by_values.json"))
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_enum_values.json")
    )

    responses = [
        {'json': enum_response},
        {'json': enum_response2},
        {'json': expected_response},
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    response = list_object_snapshots(client, first=1, object_id="a", sort_by="UNKNOWN", sort_order="Asc")
    assert response == expected_response


@pytest.mark.parametrize("first, sort_order, start_date, end_date, err_msg", [
    (0, None, None, None, ERROR_MESSAGES['INVALID_FIRST'].format(0)),
    ("a", None, None, None, validations.ERROR_MESSAGES['INVALID_NUMBER'].format("a")),
    (1, 'a', None, None, validations.ERROR_MESSAGES['INVALID_FIELD_TYPE'].format("a", "sort_order", ['Asc', 'Desc'])),
    (1, None, "2021-04-1", None, ERROR_MESSAGES['DATES_REQUIRED']),
    (1, None, None, "2021-04-1", ERROR_MESSAGES['DATES_REQUIRED']),
])
def test_list_object_snapshots_when_invalid_values_are_provided(client, requests_mock, first, sort_order, start_date, end_date, err_msg):
    """
    Tests list_object_snapshots method of PolarisClient when invalid values are provided
    """
    from rubrik_polaris.common.object import list_object_snapshots
    enum_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/snapshot_sort_by_values.json")
    )
    enum_response2 = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/sort_order_enum_values.json")
    )

    responses = [
        {'json': enum_response},
        {'json': enum_response2}
    ]

    requests_mock.post(BASE_URL + "/graphql", responses)

    with pytest.raises(ValueError) as e:
        list_object_snapshots(client, object_id="a", first=first, sort_order=sort_order, start_date=start_date,
                              end_date=end_date, sort_by="UNKNOWN")
    assert str(e.value) == err_msg



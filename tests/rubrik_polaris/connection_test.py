import pytest
import os

from rubrik_polaris.common.connection import ERROR_MESSAGES
from conftest import util_load_json, BASE_URL

QUERY_NAME = "cdm_cluster_location"


@pytest.mark.parametrize("query_name, raw_query, variables, timeout, err_msg", [
    (QUERY_NAME, None, {}, "abc", ERROR_MESSAGES['NOT_A_NUMBER'].format("abc")),
    (QUERY_NAME, None, {}, -1, ERROR_MESSAGES['INVALID_TIMEOUT'].format(-1)),
    (QUERY_NAME, "query ClusterLocationQuery()", {}, 10, ERROR_MESSAGES['INVALID_RAW_QUERY'])
])
def test_query_raw_when_invalid_values_are_provided(client, query_name, raw_query, variables, timeout, err_msg):
    """ Test case scenario when invalid values are provided """
    from rubrik_polaris.common.connection import _query_raw

    with pytest.raises(Exception) as e:
        _query_raw(client, query_name=query_name, raw_query=raw_query, variables=variables, timeout=timeout)

    assert str(e.value) == err_msg


def test_query_raw_when_valid_values_are_provided(requests_mock, client):
    """ Test case scenario when valid values are provided """
    from rubrik_polaris.common.connection import _query_raw

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/query_result.json")
    )

    requests_mock.post(BASE_URL + "/graphql", json=expected_response)
    response = _query_raw(client, query_name=QUERY_NAME, variables={})

    assert response == expected_response

    graphql_file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/raw_query.graphql"), 'r')\
        .read()
    raw_query = """{}""".format(graphql_file)
    response = _query_raw(client, query_name=QUERY_NAME, variables={}, raw_query=raw_query)

    assert response == expected_response

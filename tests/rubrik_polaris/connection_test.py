import pytest
import os

from rubrik_polaris.common.connection import ERROR_MESSAGES
from conftest import util_load_json, BASE_URL

QUERY_NAME = "cdm_cluster_location"


def test_query_raw_when_valid_values_are_provided(requests_mock, client):
    """ Test case scenario when valid values are provided """
    from rubrik_polaris.common.connection import _query_raw

    expected_response = util_load_json(
        os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/query_result.json")
    )

    requests_mock.post(BASE_URL + "/graphql", json=expected_response)
    response = _query_raw(client, raw_query=None, operation_name=None, variables={}, timeout=60)

    assert response == expected_response

    graphql_file = open(os.path.join(os.path.dirname(os.path.realpath(__file__)), "test_data/raw_query.graphql"), 'r')\
        .read()
    raw_query = """{}""".format(graphql_file)
    response = _query_raw(client, raw_query=raw_query, operation_name=None, variables={}, timeout=60)

    assert response == expected_response

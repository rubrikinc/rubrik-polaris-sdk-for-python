# Copyright 2020 Rubrik, Inc.
#
#  Permission is hereby granted, free of charge, to any person obtaining a copy
#  of this software and associated documentation files (the "Software"), to
#  deal in the Software without restriction, including without limitation the
#  rights to use, copy, modify, merge, publish, distribute, sublicense, and/or
#  sell copies of the Software, and to permit persons to whom the Software is
#  furnished to do so, subject to the following conditions:
#
#  The above copyright notice and this permission notice shall be included in
#  all copies or substantial portions of the Software.
#
#  THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
#  IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
#  FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
#  AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
#  LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
#  FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
#  DEALINGS IN THE SOFTWARE.


""" 
Collection of methods that control connection with Polaris.
"""

import requests
import http
import os
from rubrik_polaris.exceptions import RequestException, AuthenticationException, ProxyException
from rubrik_polaris.logger import logging_setup

HTTP_ERRORS = {
    400: "Bad request: An error occurred while fetching the data",
    401: "Authentication error: Please provide valid credentials",
    403: "Forbidden: Please provide valid credentials",
    404: "Resource not found",
    500: "The server encountered an error"
}

ERROR_MESSAGES = {
    "REQUEST_ERROR_WITH_PATH": "Failed request to Polaris, got {} ({}). Trace at '{}' in path {}.\nDetailed message: {}",
    "REQUEST_ERROR_WITHOUT_PATH": "Failed request to Polaris, got {} ({}). Trace at '{}'.\nDetailed message: {}",
    "REQUEST_INVALID_STATUS": "Failed request to Polaris, got {} ({}).\nDetailed message: {}",
    "NOT_A_NUMBER": "'{}' is not a valid number.",
    "INVALID_TIMEOUT": "'{}' is an invalid value for 'timeout'. Timeout must be an integer greater than 0.",
    "INVALID_RAW_QUERY": 'The query name inside the raw query should be "RubrikPolarisSDKRequest".',
    "ACCESS_TOKEN_NOT_FOUND": 'Authentication Failed: Access Token not found. Please check credentials.',
    "MFA_TOKEN_NOT_FOUND": 'Authentication Failed: Multi Factor Authentication Token not found. Please check '
                           'credentials.',
    "HOST_CONNECTION_ERROR": 'Connection Failed: Invalid host while verifying \'Polaris Account\'. Please check '
                             'domain.',
    "PROXY_ERROR": 'Proxy Error: Try removing the proxy parameter from the client or check the provided proxies.'
}


def _query_paginated(self, query_name=None, variables=None, timeout=60):
    """ Perform query against Polaris and return an iterator of entries. It
    handles responses that has more than one page of entries by requesting
    consecutive pages as entries are read from the iterator.
    """

    q = self._graphql_query_map[query_name]
    gql_query_name = q['gql_name']

    start = True
    while start or \
           (api_response['data'][gql_query_name]
            and not isinstance(api_response['data'][gql_query_name], bool)
            and 'pageInfo' in api_response['data'][gql_query_name]
            and api_response['data'][gql_query_name]['pageInfo']['hasNextPage']):
        if not start:
            variables['after'] = api_response['data'][gql_query_name]['pageInfo']['endCursor']
        api_response = self._query_raw(q['query_text'], q['operation_name'], variables, timeout)
        start = False
        nodes = self._dump_nodes(api_response)
        if isinstance(nodes, list):
            yield from nodes
        else:
            yield nodes


def _query(self, query_name=None, variables=None, timeout=60):
    """ Perform query against Polaris
    """
    q = self._graphql_query_map[query_name]
    api_response = self._query_raw(q['query_text'], q['operation_name'], variables, timeout)
    if api_response['data'].get('pageInfo'):
        raise Exception("use _query_paginated instead of _query for when expected response is paged")

    return self._dump_nodes(api_response)


def _named_raw_query(self, query_name=None, variables=None, timeout=60):
    """ Perform query against Polaris and return the raw GraphQL response.
    NOTE! This shouldn't be used in normal circumstances, use _query instead (or
    _query_paginated when the response is paginated).
    """
    q = self._graphql_query_map[query_name]
    return self._query_raw(q['query_text'], q['operation_name'], variables, timeout)


def _query_raw(self, raw_query, operation_name, variables, timeout):
    """ Perform raw GraphQL request and return the raw response in json format.
    NOTE! This shouldn't be used in normal circumstances, use _query instead (or
    _query_paginated when the response is paginated).
    """
    try:
        body = {"query": "{}".format(raw_query)}
        if variables:
            body['variables'] = variables
        if operation_name:
            body['operationName'] = operation_name

        raw_resp = requests.post(
            "{}/graphql".format(self._baseurl),
            headers=self.prepare_headers(),
            json=body,
            verify=self._verify,
            proxies=self._proxies,
            timeout=timeout
        )

        resp = raw_resp.json()
        if 'errors' in resp and len(resp['errors']) > 0:
            error = resp['errors'][0]
            self.logger.error(error)
            status_code = error['extensions']['code']
            trace_id = error['extensions'].get('trace') if error['extensions']['trace'].get('traceId', "N/A") else "N/A"
            if error.get('path'):
                raise RequestException(ERROR_MESSAGES['REQUEST_ERROR_WITH_PATH'].format(
                    status_code,
                    return_http_error_message(status_code),
                    trace_id,
                    error['path'], error['message']))
            raise RequestException(ERROR_MESSAGES['REQUEST_ERROR_WITHOUT_PATH'].format(
                status_code, return_http_error_message(status_code),
                trace_id,
                error['message']))

        if 'code' in resp and 'message' in resp and resp['code'] >= 400:
            raise RequestException(ERROR_MESSAGES['REQUEST_INVALID_STATUS'].format(resp['code'],
                return_http_error_message(resp['code']),
                resp['message']))

        raw_resp.raise_for_status()

        return resp

    except Exception as e:
        raise RequestException(e)


def _get_access_token_basic(self):
    try:
        session_url = "{}/session".format(self._baseurl)
        payload = {
            "username": self._username,
            "password": self._password
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain'
        }
        response = requests.post(
            session_url,
            json=payload,
            headers=headers,
            verify=self._verify,
            proxies=self._proxies
        )

        del payload

        response_json = response.json()
        if 'access_token' not in response_json:
            self.logger.error(ERROR_MESSAGES["ACCESS_TOKEN_NOT_FOUND"])
            raise AuthenticationException(ERROR_MESSAGES["ACCESS_TOKEN_NOT_FOUND"])
        if response_json['access_token']:
            return response_json['access_token']

        if not response_json.get('mfa_token'):
            self.logger.error(ERROR_MESSAGES["MFA_TOKEN_NOT_FOUND"])
            raise AuthenticationException(ERROR_MESSAGES["MFA_TOKEN_NOT_FOUND"])

        mfa_token = response_json['mfa_token']
        payload = {
            "username": self._username,
            "password": self._password,
            "mfa_remember_token": mfa_token
        }

        response = requests.post(
            session_url,
            json=payload,
            headers=headers,
            verify=self._verify,
            proxies=self._proxies
        )

        response_json = response.json()
        if 'access_token' not in response_json:
            self.logger.error(ERROR_MESSAGES["ACCESS_TOKEN_NOT_FOUND"])
            raise AuthenticationException(ERROR_MESSAGES["ACCESS_TOKEN_NOT_FOUND"])

        return response_json['access_token']

    except requests.exceptions.ProxyError:
        raise ProxyException(ERROR_MESSAGES['PROXY_ERROR'])
    except requests.exceptions.ConnectionError:
        raise RequestException(f"{ERROR_MESSAGES['HOST_CONNECTION_ERROR']}")
    except requests.exceptions.RequestException as request_err:
        raise RequestException(request_err)
    except ValueError as value_err:
        raise RequestException(value_err)
    except Exception as err:
        self.logger.error(err)
        raise


def _get_access_token_keyfile(self, json_key=None):
    try:
        session_url = json_key['access_token_uri']
        payload = {
            "client_id": json_key['client_id'],
            "client_secret": json_key['client_secret'],
            "name": json_key['name']
        }
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Accept': 'application/json, text/plain'
        }
        response = requests.post(
            session_url,
            json=payload,
            headers=headers,
            verify=self._verify,
            proxies=self._proxies
        )

        response_json = response.json()
        if 'access_token' not in response_json:
            self.logger.error(ERROR_MESSAGES["ACCESS_TOKEN_NOT_FOUND"])
            raise AuthenticationException(ERROR_MESSAGES["ACCESS_TOKEN_NOT_FOUND"])

        return response_json['access_token']

    except requests.exceptions.ProxyError:
        raise ProxyException(ERROR_MESSAGES['PROXY_ERROR'])
    except requests.exceptions.RequestException as request_err:
        raise RequestException(request_err)
    except ValueError as value_err:
        raise RequestException(value_err)
    except Exception as err:
        self.logger.error(err)
        raise


def return_http_error_message(status_code):
    """
    Returns HTTP error message, either custom or standard based on the status code input

    :param status_code: Error status code

    :return: Http error message
    """
    if status_code in HTTP_ERRORS.keys():
        return HTTP_ERRORS[status_code]
    else:
        return http.HTTPStatus(status_code).description


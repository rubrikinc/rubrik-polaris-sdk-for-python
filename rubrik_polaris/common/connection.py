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
import re
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


def _query(self, query_name=None, variables=None, timeout=60):
    try:
        operation_name = "SdkPython" + ''.join(w[:1].upper() + w[1:] for w in query_name.split('_'))
        query = re.sub("RubrikPolarisSDKRequest", operation_name, self._graphql_query_map[query_name]['query_text'])
        gql_query_name = self._graphql_query_map[query_name]['gql_name']
        start = True
        while start or \
                (api_response['data'][gql_query_name]
                 and not isinstance(api_response['data'][gql_query_name], bool)
                 and 'pageInfo' in api_response['data'][gql_query_name]
                 and api_response['data'][gql_query_name]['pageInfo']['hasNextPage']):
            if not start:
                variables['after'] = api_response['data'][gql_query_name]['pageInfo']['endCursor']
            api_request = requests.post(
                "{}/graphql".format(self._baseurl),
                headers=self.prepare_headers(),
                json={
                    "operationName": operation_name,
                    "variables": variables,
                    "query": "{}".format(query)
                },
                verify=self._verify,
                proxies=self._proxies,
                timeout=timeout
            )
            api_response = api_request.json()
            if 'errors' in api_response and len(api_response['errors']) >= 1:
                error = api_response['errors'][0]
                self.logger.error(error)
                status_code = error['extensions']['code']
                if error['extensions'].get('trace', ''):
                    trace_id = error['extensions']['trace']['traceId']
                else:
                    trace_id = "N/A"
                if error.get('path'):
                    raise RequestException(ERROR_MESSAGES['REQUEST_ERROR_WITH_PATH'].format(
                        status_code,
                        HTTP_ERRORS[status_code],
                        trace_id,
                        error['path'], error['message']))
                raise RequestException(
                    ERROR_MESSAGES['REQUEST_ERROR_WITHOUT_PATH'].format(
                        status_code, HTTP_ERRORS[status_code],
                        trace_id,
                        error['message']))
            elif 'code' in api_response and 'message' in api_response and api_response['code'] >= 400:
                status_code = api_response['code']
                raise RequestException(ERROR_MESSAGES['REQUEST_INVALID_STATUS'].format(status_code,
                                                                                       HTTP_ERRORS[status_code],
                                                                                       api_response['message']))
            else:
                api_request.raise_for_status()

            if start:
                out_data = self._dump_nodes(api_response)
                start = False
            else:
                out_data += self._dump_nodes(api_response)

        return out_data

    except requests.exceptions.RequestException as request_err:
        raise RequestException(request_err)
    except ValueError as value_err:
        raise RequestException(value_err)
    except Exception as err:
        raise RequestException(err)


def _query_raw(self, query_name, raw_query=None, variables=None, timeout=60):
    """
    Function to return raw response from the API based on the specified query and variables.

    :param self: client object
    :param query_name: Name of the query
    :param raw_query: Raw query for the request
    :param variables: Dictionary of variables
    :param timeout: Value of timeout for request
    :return: Response from the API
    """
    try:
        operation_name = "SdkPython" + ''.join(w[:1].upper() + w[1:] for w in query_name.split('_'))
        if raw_query:
            if "RubrikPolarisSDKRequest" not in raw_query:
                self.logger.error(ERROR_MESSAGES['INVALID_RAW_QUERY'])
                raise ValueError(ERROR_MESSAGES['INVALID_RAW_QUERY'])
            query = re.sub("RubrikPolarisSDKRequest", operation_name, raw_query)
        else:
            query = re.sub("RubrikPolarisSDKRequest", operation_name, self._graphql_query_map[query_name]['query_text'])

        try:
            timeout = int(timeout)
        except Exception:
            self.logger.error(ERROR_MESSAGES['NOT_A_NUMBER'].format(timeout))
            raise ValueError(ERROR_MESSAGES['NOT_A_NUMBER'].format(timeout))

        if timeout <= 0:
            self.logger.error(ERROR_MESSAGES['INVALID_TIMEOUT'].format(timeout))
            raise ValueError(ERROR_MESSAGES['INVALID_TIMEOUT'].format(timeout))

        api_request = requests.post(
            "{}/graphql".format(self._baseurl),
            headers=self.prepare_headers(),
            json={
                "operationName": operation_name,
                "variables": variables,
                "query": "{}".format(query)
            },
            verify=self._verify,
            proxies=self._proxies,
            timeout=timeout
        )
        api_response = api_request.json()
        if 'errors' in api_response and len(api_response['errors']) >= 1:
            error = api_response['errors'][0]
            self.logger.error(error)
            status_code = error['extensions']['code']
            if status_code >= 500:
                error_msg = HTTP_ERRORS[500]
            else:
                error_msg = HTTP_ERRORS[status_code]
            if error['extensions'].get('trace', ''):
                trace_id = error['extensions']['trace']['traceId']
            else:
                trace_id = "N/A"
            if error.get('path'):
                raise RequestException(ERROR_MESSAGES['REQUEST_ERROR_WITH_PATH'].format(
                    status_code,
                    error_msg,
                    trace_id,
                    error['path'], error['message']))
            raise RequestException(
                ERROR_MESSAGES['REQUEST_ERROR_WITHOUT_PATH'].format(
                    status_code, error_msg,
                    trace_id,
                    error['message']))
        elif 'code' in api_response and 'message' in api_response and api_response['code'] >= 400:
            status_code = api_response['code']
            raise RequestException(ERROR_MESSAGES['REQUEST_INVALID_STATUS'].format(status_code,
                                                                                   HTTP_ERRORS[status_code],
                                                                                   api_response['message']))
        else:
            api_request.raise_for_status()

        return api_response

    except requests.exceptions.RequestException as request_err:
        raise RequestException(request_err)
    except ValueError as value_err:
        raise RequestException(value_err)
    except Exception as err:
        raise RequestException(err)


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
        request = requests.post(
            session_url,
            json=payload,
            headers=headers,
            verify=self._verify,
            proxies=self._proxies
        )

        del payload

        response_json = request.json()
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

        request = requests.post(
            session_url,
            json=payload,
            headers=headers,
            verify=self._verify,
            proxies=self._proxies
        )

        response_json = request.json()
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
        request = requests.post(
            session_url,
            json=payload,
            headers=headers,
            verify=self._verify,
            proxies=self._proxies
        )

        response_json = request.json()
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

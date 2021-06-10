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

from rubrik_polaris.exceptions import PolarisException

"""
Collection of functions that manipulate GCP account components.
"""


def get_accounts_gcp(self, filter=""):
    """Retrieves GCP project information from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of GCP Projects in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_gcp"
        variables = {
            "filter": filter
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def _get_account_gcp_project_uuid_by_string(self, search_text):
    try:
        _query_name = "accounts_gcp"
        _variables = {
            "filter": search_text
        }
        return self._query(_query_name, _variables)
    except Exception as e:
        raise PolarisException("Problem getting GCP project uuid from Polaris: {}".format(search_text))


def add_project_gcp(self, service_account_auth_key_file=None, gcp_native_project_id=None, gcp_native_project_number=None, gcp_native_project_name=None):
    """Add GCP project to Polaris

    Args:
        service_account_auth_key_file (str): Filename of SA .json file
        gcp_native_project_id (str): Project_Id of GCP Project to add

        gcp_native_project_number (str): GCP Project number if ommiting SA
        gcp_native_project_name (str): GCP Project name if omitting SA

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>>  rubrik.add_project_gcp(service_account_auth_key_file="/home/peterm/.google.milanese.json", gcp_native_project_id="home-network-274622")
    """
    if service_account_auth_key_file and not gcp_native_project_name and not gcp_native_project_number:
        project = self._get_gcp_native_project(service_account_auth_key_file=service_account_auth_key_file, project_id=gcp_native_project_id)
        project['service_account_auth_key'] = open(service_account_auth_key_file, 'r').read()
    elif gcp_native_project_name and gcp_native_project_number and gcp_native_project_id and not service_account_auth_key_file:
        project = {
            "gcp_native_project_name": gcp_native_project_name,
            "gcp_native_project_number": int(gcp_native_project_number),
            "gcp_native_project_id": gcp_native_project_id
        }
    else:
        raise PolarisException("Could not add GCP Project, please checkk inputs")
    try:
        _query_name = "accounts_gcp_project_add"
        _variables = project
        _request = self._query(_query_name, _variables)
        if not _request:
            raise PolarisException("Problem adding GCP Project to Polaris: {}".format(gcp_native_project_id))
    except Exception as e:
        raise PolarisException("Problem adding GCP Project to Polaris: {}".format(gcp_native_project_id))


def delete_project_gcp(self, gcp_native_project_id=None, delete_snapshots=False):
    """Remove GCP project from Polaris

    Args:
        gcp_native_project_id (str): Project_Id of GCP Project to remove
        delete_snapshots (bool): Should snapshots be removed from Polaris

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.delete_project_gcp(gcp_native_project_id="home-network-274622")
    """
    try:
        record = self._get_account_gcp_project(search_text=gcp_native_project_id)[0]
    except Exception:
        raise PolarisException("Project does not exist in Polaris : {}".format(gcp_native_project_id))
    if record['featureDetail']['status'] == "CONNECTED":
        disable_id = self._get_account_gcp_project_uuid_by_string(str(record['project']['projectNumber']))[0]['id']
        disable_response = self._disable_account_gcp_project(project_uuid=disable_id)
        if not disable_response:
            raise PolarisException("Problem disabling protection on project: {}".format(gcp_native_project_id))
        task_results = self._monitor_task([disable_response])
        if "SUCC" in task_results['status']:
            self._delete_account_gcp_project(project_uuid=record['project']['id'])
        else:
            raise PolarisException("Failed to disable project {}".format(gcp_native_project_id))
    if "DISABLED" in record['featureDetail']['status']:
        self._delete_account_gcp_project(project_uuid=record['project']['id'])


def _disable_account_gcp_project(self, project_uuid=None, delete_snapshots=False):
    try:
        _query_name = "accounts_gcp_project_disable"
        _variables = {
            "rubrik_project_id": project_uuid,
            "delete_snapshots": delete_snapshots
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem disabling GCP Project in Polaris: {}".format(project_uuid))


def _get_account_gcp_project(self, search_text):
    try:
        _query_name = "accounts_gcp_projects"
        _variables = {
            "status_filters": [],
            "search_text": search_text
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem getting GCP Project from Polaris: {}".format(search_text))


def set_account_gcp_default_sa(self, service_account_auth_key_file=None, service_account_name=None):
    """Set default SA Key for GCP

    Args:
        service_account_auth_key_file (str): Filename of SA key file
        service_account_name (bool): Name to reference SA

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.set_account_gcp_default_sa(service_account_auth_key_file = "file.json", service_account_name = "sa-2021-03")
    """
    try:
        _query_name = "accounts_gcp_default_sa_set"
        _variables = {
            "name": service_account_name,
            "jwt_config": open(service_account_auth_key_file, 'r').read()
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem setting GCP Project default SA: {}".format(e))


def get_account_gcp_default_sa(self):
    """Get default SA Key for GCP

    Returns:
        str: Name of default GCP Service Account

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.get_account_gcp_default_sa()
    """
    try:
        _query_name = "accounts_gcp_default_sa_get"
        _request = self._query(_query_name, None)
        return _request
    except Exception as e:
        raise PolarisException("Problem getting GCP Project default SA: {}".format(e))


def _delete_account_gcp_project(self, project_uuid=None):
    try:
        _query_name = "accounts_gcp_project_delete"
        _variables = {
            "native_protection_ids": [project_uuid],
            "shared_vpc_host_project_ids": [],
            "cloud_account_project_ids": []
        }
        _request = self._query(_query_name, _variables)
    except Exception as e:
        raise PolarisException("Problem deleting GCP Project from Polaris: {}".format(project_uuid))


def _get_account_gcp_permissions_cnp(self):
    try:
        _query_name = "accounts_gcp_permissions"
        _request = self._query(_query_name, None)
        o = []
        for p in _request:
            o.append(p['permission'])
        return o
    except Exception as e:
        raise PolarisException("Problem getting GCP permission requirements from Polaris {}".format(e))


def _get_gcp_native_project(self, service_account_auth_key_file, project_id=None):
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError
    from oauth2client.service_account import ServiceAccountCredentials
    credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account_auth_key_file)
    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    # Check permissions requirement from Polaris against GCP using SA
    permission_required = self._get_account_gcp_permissions_cnp()
    permissions = {"permissions": permission_required}
    self._pp.pprint(permissions)
    try:
        request = service.projects().testIamPermissions(resource=project_id, body=permissions)
        permissions_set = request.execute()
        self._pp.pprint(permissions_set)
        permission_delta = list(set(permission_required) - set(permissions_set['permissions']))
    except HttpError as e:
        raise PolarisException("Failed to lookup SA permissions from GCP: {}".format(e))
    if len(permission_delta) > 0:
        raise PolarisException("Permissions are incorrect for Service Account. Requires additional: {}".format(permission_delta))

    # Get project details from GCP
    request = service.projects().get(projectId=project_id)
    response = request.execute()
    project = {'gcp_native_project_name': response['name'], 'gcp_native_project_id': response['projectId'], 'gcp_native_project_number': int(response['projectNumber'])}
    try:
        if response['parent']['type'] == 'organization':
            name = 'organizations/{}'.format(response['parent']['id'])
            request = service.organizations().get(name=name)
            response = request.execute()
            if 'displayName' in response:
                project['organization_name'] = response['displayName']
    except HttpError as e:
        if 'permission' in str(e):
            project['organization_name'] = response['parent']['id']
        else:
            raise PolarisException("Problem getting GCP organization: {}".format(e))
    except Exception as e:
        raise PolarisException("Problem getting GCP project details: {}".format(e))
    return project

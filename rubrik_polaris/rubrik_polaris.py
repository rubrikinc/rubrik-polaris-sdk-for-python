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

import os
import pprint
import urllib3

from .exceptions import RequestException
from .service_account import ServiceAccount, BaseUrl
from .config import get_conf_val


class PolarisClient:
    """
    There are 2 ways to create a Polaris client object:
    - from credentials, by providing domain, username and password ->
        PolarisClient.from_credentials()
    - with a service account, either with a ServiceAccount object or
      a service account JSON file ->
        PolarisClient.from_service_account()
        PolarisClient.from_service_account_file()

    """
    # Public
    from .common.core import get_sla_domains, submit_on_demand, submit_assign_sla, get_task_status, \
        get_snapshots, get_event_series_list, get_report_data, get_polaris_version
    from .accounts.aws import get_accounts_aws, get_accounts_aws_detail, get_account_aws_native_id, add_account_aws, \
        delete_account_aws
    from .accounts.azure import get_accounts_azure_native, add_account_azure, delete_account_azure, \
        set_account_azure_default_sa, get_accounts_azure_cloud
    from .accounts.gcp import get_accounts_gcp, add_project_gcp, delete_project_gcp, \
        get_account_gcp_default_sa, set_account_gcp_default_sa
    from .compute.ec2 import get_compute_object_ids_ec2, get_compute_ec2, submit_compute_export_ec2, \
        submit_compute_restore_ec2
    from .compute.azurevm import get_compute_object_ids_azure, get_compute_azure, submit_compute_restore_azure
    from .compute.gce import get_compute_object_ids_gce, get_compute_gce, submit_compute_restore_gce
    from .compute.vsphere import get_compute_vsphere, get_compute_object_ids_vsphere
    from .storage.ebs import get_storage_object_ids_ebs, get_storage_ebs
    from .common.graphql import get_enum_values
    from .cluster import get_cdm_cluster_location, get_cdm_cluster_connection_status
    from .appflows import get_appflows_blueprints

    # Private
    from .common.connection import _query, _get_access_token_basic, _get_access_token_keyfile
    from .common.validations import _validate
    from .compute.ec2 import _get_aws_region_vpcs, _get_aws_region_kmskeys, _get_aws_region_sshkeypairs
    from .compute.common import _submit_compute_restore, _get_compute_object_ids, _submit_compute_export
    from .common.monitor import _monitor_job, _monitor_threader, _monitor_task
    from .common.graphql import _dump_nodes, _get_details_from_graphql_query
    from .common.core import _get_snapshot
    from .accounts.aws import _invoke_account_delete_aws, _invoke_aws_stack, _commit_account_delete_aws, \
        _update_account_aws, \
        _destroy_aws_stack, _disable_account_aws, _get_aws_profiles, _add_account_aws, _delete_account_aws, \
        _update_account_aws_initiate, _get_account_map_aws
    from .accounts.gcp import _get_gcp_native_project, _delete_account_gcp_project, \
        _disable_account_gcp_project, _get_account_gcp_project, _get_account_gcp_permissions_cnp, \
        _get_account_gcp_project_uuid_by_string
    from .accounts.azure import _get_native_subscription_id_and_name, _get_accounts_azure_permission_version
    from .common.connection import _get_access_token_keyfile, _get_access_token_basic

    def __init__(
            self,
            domain=None,
            username=None,
            password=None,
            json_keyfile=None,
            **kwargs):
        from .common.graphql import _build_graphql_maps
        self._pp = pprint.PrettyPrinter(indent=4)

        # Set base variables
        self._kwargs = kwargs
        self._data_path = "{}/graphql/".format(os.path.dirname(os.path.realpath(__file__)))

        # Switch off SSL checks if needed
        if self._kwargs.get('insecure', False):
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        if 'service_account' in kwargs:
            sa: ServiceAccount = kwargs['service_account']
            self._baseurl = sa.baseurl
            self._access_token = sa.get_client_token()
        elif json_keyfile is not None:
            sa: ServiceAccount = ServiceAccount.from_json_file(json_keyfile)
            self._baseurl = sa.baseurl
            self._access_token = sa.get_client_token()
        else:
            # from credentials
            domain = get_conf_val('domain', domain)
            username = get_conf_val('username', username)
            password = get_conf_val('password', password)
            # Adjust Polaris domain if a custom root is defined
            root_domain = get_conf_val('root_domain',
                                       self._kwargs.get('root_domain'),
                                       'my.rubrik.com')
            self._baseurl = BaseUrl.from_domain(domain, root_domain).baseurl
            self._access_token = self._get_access_token_basic(username, password)

        self._headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            'Authorization': 'Bearer ' + self._access_token
        }
        # Get graphql content
        (self._graphql_query_map) = _build_graphql_maps(self)

    @classmethod
    def from_service_account(cls, service_account: ServiceAccount, **kwargs):
        return PolarisClient(
            service_account=service_account,
            **kwargs)

    @classmethod
    def from_service_account_file(cls, path, **kwargs):
        return PolarisClient(
            service_account=ServiceAccount.from_json_file(path),
            **kwargs)

    @classmethod
    def from_credentials(cls, username: str, password: str, domain: str,
                         **kwargs):
        return PolarisClient(domain, username, password, **kwargs)

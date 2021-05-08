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


class PolarisClient:
    # Public
    from .lib.common.core import get_sla_domains, submit_on_demand, submit_assign_sla, get_task_status, \
        get_snapshots, get_event_series_list, get_report_data
    from .lib.accounts.aws import get_accounts_aws, get_accounts_aws_detail, get_account_aws_native_id, add_account_aws, delete_account_aws
    from .lib.accounts.azure import get_accounts_azure
    from .lib.accounts.gcp import get_accounts_gcp, add_project_gcp, delete_project_gcp, \
        get_account_gcp_default_sa, set_account_gcp_default_sa
    from .lib.compute.ec2 import get_compute_object_ids_ec2, get_compute_ec2, submit_compute_export_ec2, submit_compute_restore_ec2
    from .lib.compute.azurevm import get_compute_object_ids_azure, get_compute_azure, submit_compute_restore_azure
    from .lib.compute.gce import get_compute_object_ids_gce, get_compute_gce, submit_compute_restore_gce
    from .lib.compute.vsphere import get_compute_vsphere, get_compute_object_ids_vsphere
    from .lib.storage.ebs import get_storage_object_ids_ebs, get_storage_ebs
    from .lib.common.graphql import get_enum_values
    from .lib.cluster import get_cdm_cluster_location, get_cdm_cluster_connection_status

    # Private
    from .lib.common.connection import _query, _get_access_token_basic, _get_access_token_keyfile
    from .lib.common.validations import _validate
    from .lib.compute.ec2 import _get_aws_region_vpcs, _get_aws_region_kmskeys, _get_aws_region_sshkeypairs
    from .lib.compute.common import _submit_compute_restore, _get_compute_object_ids, _submit_compute_export
    from .lib.common.monitor import _monitor_job, _monitor_threader, _monitor_task
    from .lib.common.graphql import _dump_nodes, _get_details_from_graphql_query
    from .lib.common.core import _get_snapshot
    from .lib.accounts.aws import _invoke_account_delete_aws, _invoke_aws_stack, _commit_account_delete_aws, _update_account_aws, \
        _destroy_aws_stack, _disable_account_aws, _get_aws_profiles, _add_account_aws, _delete_account_aws, \
        _update_account_aws_initiate, _get_account_map_aws
    from .lib.accounts.gcp import _get_gcp_native_project, _delete_account_gcp_project, \
        _disable_account_gcp_project, _get_account_gcp_project, _get_account_gcp_permissions_cnp, _get_account_gcp_project_uuid_by_string
    from .lib.common.connection import _get_access_token_keyfile, _get_access_token_basic

    def __init__(self, domain=None, username=None, password=None, json_keyfile=None, **kwargs):
        from .lib.common.graphql import _build_graphql_maps

        self._pp = pprint.PrettyPrinter(indent=4)

        # Set credentials
        self._domain = self._get_cred('rubrik_polaris_domain', domain)
        self._username = self._get_cred('rubrik_polaris_username', username)
        self._password = self._get_cred('rubrik_polaris_password', password)

        if not (self._domain and self._username and self._password) and not json_keyfile:
            raise Exception('Required credentials are missing! Please pass in username, password and domain, directly or through the OS environment, or .json key file.')

        # Set base variables
        self._kwargs = kwargs
        self._data_path = "{}/graphql/".format(os.path.dirname(os.path.realpath(__file__)))

        # Switch off SSL checks if needed
        if 'insecure' in self._kwargs and self._kwargs['insecure']:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Adjust Polaris domain if a custom root is defined
        if 'root_domain' in self._kwargs and self._kwargs['root_domain'] is not None:
            self._baseurl = "https://{}.{}/api".format(self._domain, self._kwargs['root_domain'])
        else:
            self._baseurl = "https://{}.my.rubrik.com/api".format(self._domain)

        try:
            if self._username and self._password:
                self._access_token = self._get_access_token_basic()
                del(self._username, self._password)
            elif json_keyfile:
                import json
                import re
                with open(json_keyfile) as f:
                    json_key = json.load(f)
                self._baseurl = re.sub(r"/client_token", "", json_key['access_token_uri'])
                self._access_token = self._get_access_token_keyfile(json_key=json_key)

            self._headers = {
                'Content-Type': 'application/json',
                'Accept': 'application/json',
                'Authorization': 'Bearer ' + self._access_token
            }
            # Get graphql content
            (self._graphql_query_map) = _build_graphql_maps(self)

        except RequestException as err:
            raise
        except OSError as os_err:
            raise
        except Exception as e:
            raise

    @staticmethod
    def _get_cred(env_key, override=None):
        cred = None

        if env_key in os.environ:
            cred = os.environ[env_key]

        if override:
            cred = override

        return cred

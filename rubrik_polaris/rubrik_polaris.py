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
import re
import sys
import json
import logging
from .exceptions import RequestException
from .logger import logging_setup

"""Instantiates Polaris connection context
Args:
    domain (str): Polaris domain identifier.
    username (str): Polaris username
    password (str): Polaris password
    root_domain (str): Polaris root domain only if not *.my.rubrik.com
    insecure (bool): Allow unverified SSL keys
    json_keyfile (str): Service account credential file (used exclusive of first 4 options.
Returns:
    object: Polaris connection context
Raises:
    RequestException: If the query to Polaris returned an error
"""
class PolarisClient:
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
    from .common.validations import check_first_arg, to_boolean, validate_id, check_enum
    from .common.object import list_vm_objects, search_object, get_object_metadata, get_object_snapshot
    from .sonar.policy import list_policy_analyzer_groups, list_policies
    from .sonar.scan import trigger_on_demand_scan, get_on_demand_scan_status, get_on_demand_scan_result
    from .sonar.object import get_sensitive_hits_object_list, get_sensitive_hits_object_detail, get_sensitive_hits
    from .radar.csv import get_csv_result
    from .sonar.csv import get_csv_download, get_csv_result_download
    from .gps.files import get_snapshot_files, request_download_snapshot_files
    from .gps.vm import create_vm_snapshot, create_vm_livemount, create_vm_livemount_v2, list_vsphere_hosts, export_vm_snapshot, \
        list_vsphere_datastores, get_async_request_result, recover_vsphere_vm_files
    from .gps.sla import list_sla_domains
    from .gps.cluster import list_clusters
    from .radar.anomaly import get_analysis_status
    from .radar.ioc import trigger_ioc_scan, get_ioc_scan_list, get_ioc_scan_result
    from .common.core import list_event_series
    from .common.object import list_objects
    from .common.object import list_object_snapshots
    from .k8s.cluster import create_k8s_cluster, refresh_k8s_cluster, list_k8s_clusters, get_k8s_status
    from .k8s.namespace import get_k8s_namespaces, get_k8s_namespace

    # Private
    from .common.connection import _query, _query_paginated, _query_raw, _named_raw_query, _get_access_token_basic, _get_access_token_keyfile
    from .common.validations import _validate
    from .compute.ec2 import _get_aws_region_vpcs, _get_aws_region_kmskeys, _get_aws_region_sshkeypairs
    from .compute.common import _submit_compute_restore, _get_compute_object_ids, _submit_compute_export
    from .common.monitor import _monitor_job, _monitor_threader, _monitor_task
    from .common.graphql import _dump_nodes, _get_details_from_graphql_query
    from .common.core import _get_snapshot
    from .common.user import get_user_downloads
    from .accounts.aws import _invoke_account_delete_aws, _invoke_aws_stack, _commit_account_delete_aws, \
        _update_account_aws, \
        _destroy_aws_stack, _disable_account_aws, _get_aws_profiles, _add_account_aws, _delete_account_aws, \
        _update_account_aws_initiate, _get_account_map_aws
    from .accounts.gcp import _get_gcp_native_project, _delete_account_gcp_project, \
        _disable_account_gcp_project, _get_account_gcp_project, _get_account_gcp_permissions_cnp, \
        _get_account_gcp_project_uuid_by_string
    from .accounts.azure import _get_native_subscription_id_and_name, _get_accounts_azure_permission_version
    from .common.connection import _get_access_token_keyfile, _get_access_token_basic

    def __init__(self, domain=None, username=None, password=None, json_keyfile=None,
                 logging_handler=logging.NullHandler(), logging_level=logging.WARNING, **kwargs):
        from .common.graphql import _build_graphql_maps

        self._pp = pprint.PrettyPrinter(indent=4)

        self.logger = logging_setup(logging_handler, logging_level)

        # Set credentials
        self._domain = self._get_cred('rubrik_polaris_domain', domain)
        self._username = self._get_cred('rubrik_polaris_username', username)
        self._password = self._get_cred('rubrik_polaris_password', password)
        self._verify = not kwargs.get('insecure', False)
        self._proxies = kwargs.get('proxies')
        self._json_data = kwargs.get('json_data')
        self._json_keyfile = json_keyfile

        if (not self._domain or not self._username or not self._password) and not json_keyfile \
                and not self._json_data:
            self.logger.critical("Required credentials are missing!")
            raise Exception('Required credentials are missing! Please pass in username, password and domain, directly'
                            ' or through the OS environment, or .json key file, or JSON data.')

        # Set base variables
        self._kwargs = kwargs
        self._data_path = "{}/common/graphql/".format(os.path.dirname(os.path.realpath(__file__)))

        # Switch off SSL checks if needed
        if 'insecure' in self._kwargs and self._kwargs['insecure']:
            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # Adjust Polaris domain if a custom root is defined
        if 'root_domain' in self._kwargs and self._kwargs['root_domain'] is not None:
            self._baseurl = "https://{}.{}/api".format(self._domain, self._kwargs['root_domain'])
        else:
            self._baseurl = "https://{}.my.rubrik.com/api".format(self._domain)

        try:
            self._access_token = None
            self._user_agent = self._kwargs.get('user_agent')
            self._headers = {}

            if self._json_keyfile:
                with open(self._json_keyfile) as f:
                    json_key = json.load(f)
                self._baseurl = re.sub(r"/client_token", "", json_key['access_token_uri'])

            elif self._json_data:
                json_data = json.loads(self._json_data)
                self._baseurl = re.sub(r"/client_token", "", json_data['access_token_uri'])

            # Get graphql content
            (self._graphql_query_map) = _build_graphql_maps(self)

        except RequestException as err:
            raise
        except OSError as os_err:
            raise
        except Exception as e:
            self.logger.error(e)
            raise

    @staticmethod
    def _get_cred(env_key, override=None):
        cred = None

        if env_key in os.environ:
            cred = os.environ[env_key]

        if override:
            cred = override

        return cred

    def authenticate(self):
        if self._json_keyfile:
            with open(self._json_keyfile) as f:
                json_key = json.load(f)
            self._access_token = self._get_access_token_keyfile(json_key=json_key)
            self.logger.info("Retrieved access token using json key file.")

        elif self._json_data:
            json_data = json.loads(self._json_data)
            self._access_token = self._get_access_token_keyfile(json_key=json_data)
            self.logger.info("Retrieved access token using json data.")

        elif self._username and self._password:
            self._access_token = self._get_access_token_basic()
            del (self._username, self._password)
            self.logger.info("Retrieved access token using username and password.")

        return self._access_token

    def prepare_headers(self):
        if self._user_agent:
            self._headers['User-Agent'] = self._user_agent
        self._headers['Content-Type'] = 'application/json'
        self._headers['Accept'] = 'application/json'

        if self._access_token:
            self._headers['Authorization'] = 'Bearer ' + self._access_token
        else:
            self._headers['Authorization'] = 'Bearer ' + self.authenticate()

        return self._headers

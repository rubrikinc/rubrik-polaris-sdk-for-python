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
Collection of functions that manipulate Azure account components.
"""


def get_accounts_azure_native(self, filter=""):
    """Retrieves Azure native account information from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of Azure native accounts in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_azure_native"
        variables = {
            "filter": filter
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def get_accounts_azure_cloud(self, cloud_account_features="CLOUD_NATIVE_PROTECTION"):
    """Retrieves Azure cloud account information from Polaris

    Args:
        cloud_account_features (str): Feature string to filter results

    Returns:
        dict: Details of Azure cloud accounts in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_azure_cloud"
        variables = {
            "cloud_account_features": cloud_account_features
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def set_account_azure_default_sa(
        self,
        azure_app_id=None,
        azure_app_secret_key=None,
        azure_app_tenant_id=None,
        azure_app_name=None,
        azure_tenant_domain_name=None,
        azure_cloud_type='AZUREPUBLICCLOUD'):

    """Set default SA for Azure
    Args:
        azure_app_id (str):  Client ID of the Application
        azure_app_secret_key (str):  Client secret key of the Application.
        azure_app_tenant_id (str): Optional, ID of the home tenant of the application.
        azure_app_name (str): Optional, Name of the application
        azure_tenant_domain_name (str): Optional, Domain Name of the Azure tenant.
        azure_cloud_type (str): AZUREPUBLICCLOUD [default] or AZURECHINACLOUD
    Returns:
        dict: Status if unsuccessful
    Raises:
        RequestException: If the query to Polaris returned an error
    Examples:
    """
    try:
        _query_name = "accounts_azure_default_sa_set"
        self._validate(
            mutation_name=_query_name,
            azure_cloud_type=azure_cloud_type
        )
        _variables = {
            "azure_app_id": azure_app_id,
            "azure_app_secret_key": azure_app_secret_key,
            "azure_app_tenant_id": azure_app_tenant_id,
            "azure_app_name": azure_app_name,
            "azure_tenant_domain_name": azure_tenant_domain_name,
            "azure_cloud_type": self.azure_cloud_type
        }
        _request = self._query(self.mutation_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem setting Azure App default SA: {}".format(e))


def add_account_azure(
        self,
        azure_tenant_domain_name=None,
        azure_cloud_type='AZUREPUBLICCLOUD',
        cloud_account_features='CLOUD_NATIVE_PROTECTION',
        azure_subscription_id=None,
        azure_subscription_name=None,
        azure_regions=None,
        azure_policy_version=1007):
    """Add Azure subscription to Polaris
    Args:
        azure_tenant_domain_name (str): Optional, Domain Name of the Azure tenant.
        azure_cloud_type (str): AZUREPUBLICCLOUD [default] or AZURECHINACLOUD
        cloud_account_features (str): Polaris cloud feature - CLOUDNATIVEPROTECTION [default]
        azure_subscriptions (arr): Array of [["subscription_id","subscription_name"],[...]]
        azure_regions (arr): Array of Azure Regions
        azure_policy_version (int): Azure Policy version
    Returns:
        dict: Status if unsuccessful
    Raises:
        RequestException: If the query to Polaris returned an error
    Examples:
    """
    try:
        _query_name = "accounts_azure_add"
        self._validate(
            mutation_name=_query_name,
            azure_cloud_type=azure_cloud_type,
            cloud_account_features=cloud_account_features,
            azure_regions=azure_regions,
#            azure_subscriptions=azure_subscriptions
        )

        azure_subscriptions_converted = [{'nativeId': azure_subscription_id, 'name': azure_subscription_name}]

        _variables = {
            "azure_tenant_domain_name": azure_tenant_domain_name,
            "azure_cloud_type": self.azure_cloud_type,
            "feature": self.cloud_account_features,
            "azure_subscriptions": azure_subscriptions_converted,
            "azure_regions": self.azure_regions,
            "azure_policy_version": azure_policy_version
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem adding Azure Subscription: {}".format(e))


def _get_native_subscription_id_and_name(self, azure_subscription_id=None, cloud_account_features=None):
    azure_tenants = self.get_accounts_azure_cloud(cloud_account_features=cloud_account_features)
    for tenant in azure_tenants:
        for azure_subscription in tenant['subscriptions']:
            if azure_subscription['featureDetail']['feature'] == cloud_account_features \
                    and azure_subscription['nativeId'] == azure_subscription_id:
                return azure_subscription['id'], azure_subscription['name']


def delete_account_azure(
        self,
        cloud_account_features='CLOUD_NATIVE_PROTECTION',
        azure_subscription_id=None,
        delete_snapshots=False):
    """Add Azure subscription to Polaris
    Args:
        cloud_account_features (str): Polaris cloud feature - CLOUDNATIVEPROTECTION [default]
        azure_subscription_id (string): Subscription ID from Azure
        delete_snapshots (bool): Delete Rubrik snapshots for subscription [default: False]
    Returns:
        dict: Status if unsuccessful
    Raises:
        RequestException: If the query to Polaris returned an error
    Examples:
    """
    polaris_native_subscription_id = None
    try:
        # Get ID to delete subscription
        polaris_subscription_id, polaris_subscription_name = \
            self._get_native_subscription_id_and_name(azure_subscription_id=azure_subscription_id, \
                                                      cloud_account_features=cloud_account_features)

        # Get ID to disable subscription
        suspect_subscriptions = self.get_accounts_azure_native(filter=polaris_subscription_name)
        for subscription in suspect_subscriptions:
            if subscription['native_id'] == azure_subscription_id:
                polaris_native_subscription_id = subscription['id']
    except Exception as e:
        raise PolarisException("Problem mapping IDs required to remove subscription")

    # Disable subscription in Polaris
    if polaris_native_subscription_id:
        try:
            _query_name = "accounts_azure_disable_subscription"
            _variables = {
                "delete_snapshots": delete_snapshots,
                "azure_subscription_id": polaris_native_subscription_id
            }
            response = self._query(_query_name, _variables)
            results = self._monitor_task(response)
        except Exception as e:
            raise PolarisException("Problem disabling Azure Subscription: {}".format(e))

    # Delete subscription in Polaris
    try:
        _query_name = "accounts_azure_delete_subscription"
        self._validate(
            cloud_account_features=cloud_account_features,
        )
        _variables = {
            "cloud_account_features": self.cloud_account_features,
            "azure_subscription_ids": [polaris_subscription_id]
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem deleting Azure Subscription: {}".format(e))

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


def get_accounts_azure(self, filter=""):
    """Retrieves Azure account information from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of Azure accounts in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_azure"
        variables = {
            "filter": filter
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
        feature='CLOUD_NATIVE_PROTECTION',
        azure_subscriptions=None,
        azure_regions=None,
        azure_policy_version=None):
    """Add Azure subscription to Polaris
    Args:
        azure_tenant_domain_name (str): Optional, Domain Name of the Azure tenant.
        azure_cloud_type (str): AZUREPUBLICCLOUD [default] or AZURECHINACLOUD
        feature (str): Polaris cloud feature - CLOUDNATIVEPROTECTION [default]
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
            feature=feature,
            azure_regions=azure_regions,
#            azure_subscriptions=azure_subscriptions
        )

        azure_subscriptions_converted = []
        for azure_subscription in azure_subscriptions:
            azure_subscriptions_converted.append({'nativeId': azure_subscription[0], 'name': azure_subscription[1]})

        _variables = {
            "azure_tenant_domain_name": azure_tenant_domain_name,
            "azure_cloud_type": self.azure_cloud_type,
            "feature": self.feature,
            "azure_subscriptions": azure_subscriptions_converted,
            "azure_regions": self.azure_regions,
            "azure_policy_version": azure_policy_version
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem adding Azure Subscription: {}".format(e))


def delete_account_azure(
        self,
        feature='CLOUDNATIVEPROTECTION',
        azure_subscription_ids=None):
    """Add Azure subscription to Polaris
    Args:
        feature (str): Polaris cloud feature - CLOUDNATIVEPROTECTION [default]
        azure_subscription_ids (arr): Array of ["polaris_subscription_id", ...]
    Returns:
        dict: Status if unsuccessful
    Raises:
        RequestException: If the query to Polaris returned an error
    Examples:
    """
    try:
        _query_name = "accounts_azure_delete"
        self._validate(
            mutation_name=_query_name,
            feature=feature,
            azure_subscription_ids=azure_subscription_ids
        )
        _variables = {
            "feature": self.feature,
            "azure_subscription_ids": self.azure_subscription_ids
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem deleting Azure Subscription: {}".format(e))
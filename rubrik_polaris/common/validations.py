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

from rubrik_polaris.exceptions import ValidationException
from uuid import UUID


def _validate(self, **kwargs):
    for validation in kwargs:
        if not kwargs[validation]:
            kwargs[validation] = "NONE"
        if isinstance(kwargs[validation], list):
            for test in kwargs[validation]:
                setattr(self, validation, globals()['_' + validation + '_validation'](self, test_variable=test))
        else:
            setattr(self, validation, globals()['_' + validation + '_validation'](self, test_variable=kwargs[validation]))


def _mutation_name_validation(self, test_variable=None):
    if test_variable not in self._graphql_query_map:
        raise ValidationException("mutation_name not found : {}".format(test_variable))
    return test_variable


def _query_name_validation(self, test_variable=None):
    if test_variable not in self._graphql_query_map:
        raise ValidationException("query_name not found : {}".format(test_variable))
    return test_variable


def _aws_native_account_id_validation(self, test_variable=None):
    self.aws_account_map = self._get_account_map_aws()
    for aws_account in self.aws_account_map:
        if self.aws_account_map[aws_account]['id'] == test_variable:
            return test_variable
    raise ValidationException("aws_native_account_id not found: {}".format(test_variable))


def _aws_account_number_validation(self, test_variable=None):
    self.aws_account_map = self._get_account_map_aws()
    connected_accounts = []
    if not test_variable or test_variable not in self.aws_account_map or self.aws_account_map[test_variable]['status'].lower() != 'connected':
        for account in self.aws_account_map:
            if self.aws_account_map[account]['status'].lower() == 'connected':
                connected_accounts.append(account)
        raise ValidationException("{} not found or not connected, valid account numbers are {}".format(test_variable, connected_accounts))
    return test_variable


def _snapshot_id_validation(self, test_variable=None):
    if not test_variable:
        raise ValidationException("snapshot_id not specified : {}".format(test_variable))

    try:
        self.snapshot_details = self._get_snapshot(snapshot_id=test_variable)
        if self.snapshot_details['isCorrupted']:
            raise ValidationException("snapshot_id appears to be corrupted : {}".format(test_variable))
        if self.snapshot_details['isDeletedFromSource']:
            raise ValidationException("snapshot_id has been deleted from the source : {}".format(test_variable))
        if self.snapshot_details['isExpired']:
            raise ValidationException("snapshot_id is expired : {}".format(test_variable))
    except Exception as e:
        raise ValidationException("not a valid snapshot_id : {}".format(test_variable))
    return test_variable


def _aws_regions_validation(self, test_variable=None):
    regions = self.get_enum_values(name="AwsNativeRegionEnum")
    if not test_variable or test_variable not in regions:
        raise ValidationException("{} not found, valid regions are {}".format(test_variable, list(regions)))
    return test_variable


def _aws_instance_type_validation(self, test_variable=None):
    instance_details = self.get_compute_ec2(object_id=self.snapshot_details['snappableId'])
    instance_types = self.get_enum_values(name="AwsNativeEc2InstanceTypeEnum")
    if not test_variable or test_variable not in instance_types:
        self.instance_type = instance_details['instanceType']


def _aws_instance_name_validation(self, test_variable=None):
    instance_details = self.get_compute_ec2(object_id=self.snapshot_details['snappableId'])
    if not test_variable:
        self.instance_name = instance_details['instanceName']


def _aws_vpc_validation(self, test_variable=None):
    self.aws_vpcs = self._get_aws_region_vpcs(self.aws_region, self.aws_account_map[self.aws_account_number]['id'])
    if not test_variable or test_variable not in self.aws_vpcs:
        raise ValidationException("{} not found, valid vpcs are {}".format(test_variable, list(self.aws_vpcs)))
    return test_variable


def _aws_subnet_validation(self, test_variable=None):
    if not test_variable or test_variable not in self.aws_vpcs[self.aws_vpc]['subnets']:
        raise ValidationException("{} not found, valid subnets are {}".format(test_variable, list(self.aws_vpcs[self.aws_vpc]['subnets'])))
    return test_variable


def _aws_security_group_validation(self, test_variable=None):
    if not test_variable or test_variable not in self.aws_vpcs[self.aws_vpc]['security_groups']:
        raise ValidationException("{} not found, valid security_groups are {}".format(test_variable, list(self.aws_vpcs[self.aws_vpc]['security_groups'])))
    return test_variable


def _copy_tags_validation(self, test_variable=None):
    if not test_variable:
        test_variable = True
    return test_variable


def _use_replica_validation(self, test_variable=None):
    if not test_variable:
        test_variable = False
    return test_variable


def _azure_cloud_type_validation(self, test_variable=None):
    test = self.get_enum_values(name="AzureCloudTypeEnum")
    if not test_variable or test_variable not in test:
        raise ValidationException("{} not found, valid cloud types are {}".format(test_variable, list(test)))
    return test_variable


def _azure_regions_validation(self, test_variable=None):
    test = self.get_enum_values(name="AzureCloudAccountRegionEnum")
    if not test_variable or test_variable not in test:
        raise ValidationException("{} not found, valid regions are {}".format(test_variable, list(test)))
    return test_variable


def _cloud_account_action_validation(self, test_variable=None):
    test = self.get_enum_values(name="CloudAccountActionEnum")
    if not test_variable or test_variable not in test:
        raise ValidationException("{} not found, valid features are {}".format(test_variable, list(test)))
    return test_variable


def _cloud_account_features_validation(self, test_variable=None):
    test = self.get_enum_values(name="CloudAccountFeatureEnum")
    if not test_variable or test_variable not in test:
        raise ValidationException("{} not found, valid features are {}".format(test_variable, list(test)))
    return test_variable


def _uuid_validation(self, test_variable=None):
    if not UUID(test_variable):
        raise ValidationException("{} not a UUID".format(test_variable))
    return test_variable


def _azure_subscription_ids(self, test_variable=None):
    if not test_variable:
        raise ValidationException("No subscription ids in list")
    if not _uuid_validation(test_variable=test_variable):
        raise ValidationException("{} is not a UUID".format(test_variable))
    return test_variable
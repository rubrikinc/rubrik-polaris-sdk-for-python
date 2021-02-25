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


def _validate(self, **kwargs):
    for validation in kwargs:
        globals()[validation+'_validation'](self, test_variable=kwargs[validation])


def mutation_name_validation(self, test_variable=None):
    if test_variable not in self._graphql_query_map:
        raise ValidationException("mutation_name not found : {}".format(test_variable))
    self.mutation_name = test_variable


def query_name_validation(self, test_variable=None):
    if test_variable not in self._graphql_query_map:
        raise ValidationException("query_name not found : {}".format(test_variable))
    self.query_name = test_variable
    


def aws_native_account_id_validation(self, test_variable=None):
    self.aws_account_map = self._get_account_map_aws()
    for aws_account in self.aws_account_map:
        if self.aws_account_map[aws_account]['id'] == test_variable:
            self.aws_native_account_id = test_variable
            return
    raise ValidationException("aws_native_account_id not found: {}".format(test_variable))


def aws_account_number_validation(self, test_variable=None):
    self.aws_account_map = self._get_account_map_aws()
    connected_accounts = []
    if not test_variable or test_variable not in self.aws_account_map or self.aws_account_map[test_variable]['status'].lower() != 'connected':
        for account in self.aws_account_map:
            if self.aws_account_map[account]['status'].lower() == 'connected':
                connected_accounts.append(account)
        raise ValidationException("account_number not found or not connected, valid account numbers are {}".format(connected_accounts))
    self.aws_account_number = test_variable


def snapshot_id_validation(self, test_variable=None):
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
    self.snapshot_id = test_variable


def aws_region_validation(self, test_variable=None):
    regions = self.get_enum_values(name="AwsNativeRegionEnum")
    if not test_variable or test_variable not in regions:
        raise ValidationException("region not found, valid regions are {}".format(list(regions)))
    self.aws_region = test_variable


def aws_instance_type_validation(self, test_variable=None):
    instance_details = self.get_compute_ec2(object_id=self.snapshot_details['snappableId'])
    instance_types = self.get_enum_values(name="AwsNativeEc2InstanceTypeEnum")
    if not test_variable or test_variable not in instance_types:
        self.instance_type = instance_details['instanceType']
    self.aws_instance_type = test_variable


def aws_instance_name_validation(self, test_variable=None):
    instance_details = self.get_compute_ec2(object_id=self.snapshot_details['snappableId'])
    if not test_variable:
        self.instance_name = instance_details['instanceName']
    self.aws_instance_name = test_variable


def aws_vpc_validation(self, test_variable=None):
    self.aws_vpcs = self._get_aws_region_vpcs(self.aws_region, self.aws_account_map[self.aws_account_number]['id'])
    if not test_variable or test_variable not in self.aws_vpcs:
        raise ValidationException("vpc not found, valid vpcs are {}".format(list(self.aws_vpcs)))
    self.aws_vpc = test_variable


def aws_subnet_validation(self, test_variable=None):
    if not test_variable or test_variable not in self.aws_vpcs[self.aws_vpc]['subnets']:
        raise ValidationException("subnet not found, valid subnets are {}".format(list(self.aws_vpcs[self.aws_vpc]['subnets'])))
    self.aws_subnet = test_variable


def aws_security_group_validation(self, test_variable=None):
    for sg in test_variable:
        if not sg or sg not in self.aws_vpcs[self.aws_vpc]['security_groups']:
            raise ValidationException("security_group not found, valid security_groups are {}".format(list(self.aws_vpcs[self.aws_vpc]['security_groups'])))
    self.aws_security_group = test_variable


def copy_tags_validation(self, test_variable=None):
    if not test_variable:
        test_variable = True
    self.copy_tags = test_variable


def use_replica_validation(self, test_variable=None):
    if not test_variable:
        test_variable = False
    self.use_replica = test_variable

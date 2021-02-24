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
        globals()[validation+'_validation'](self, input=kwargs[validation])


def mutation_name_validation(self, input=None):
    if input not in self._graphql_query_map:
        raise ValidationException("Mutation not found : {}".format(input))
    self.mutation_name = input


def query_name_validation(self, input=None):
    if input not in self._graphql_query_map:
        raise ValidationException("Mutation not found : {}".format(input))
    self.query_name = input


def aws_account_number_validation(self, input=None):
    self.aws_account_map = self._get_account_map_aws()
    connected_accounts = []
    if not input or input not in self.aws_account_map or self.aws_account_map[input]['status'].lower() != 'connected':
        for account in self.aws_account_map:
            if self.aws_account_map[account]['status'].lower() == 'connected':
                connected_accounts.append(account)
        raise ValidationException("account_number not found or not connected, valid account numbers are {}".format(connected_accounts))
    self.aws_account_number = input


def snapshot_id_validation(self, input=None):
    if not input:
        raise ValidationException("snapshot_id not specified : {}".format(input))

    try:
        self.snapshot_details = self._get_snapshot(snapshot_id=input)
        if self.snapshot_details['isCorrupted']:
            raise ValidationException("snapshot_id appears to be corrupted : {}".format(input))
        if self.snapshot_details['isDeletedFromSource']:
            raise ValidationException("snapshot_id has been deleted from the source : {}".format(input))
        if self.snapshot_details['isExpired']:
            raise ValidationException("snapshot_id is expired : {}".format(input))
    except Exception as e:
        raise ValidationException("not a valid snapshot_id : {}".format(input))
    self.snapshot_id = input


def aws_region_validation(self, input=None):
    regions = self.get_enum_values(name="AwsNativeRegionEnum")
    if not input or input not in regions:
        raise ValidationException("region not found, valid regions are {}".format(list(regions)))
    self.aws_region = input


def aws_instance_type_validation(self, input=None):
    instance_details = self.get_compute_ec2(object_id=self.snapshot_details['snappableId'])
    instance_types = self.get_enum_values(name="AwsNativeEc2InstanceTypeEnum")
    if not input or input not in instance_types:
        self.instance_type = instance_details['instanceType']
    self.aws_instance_type = input


def aws_instance_name_validation(self, input=None):
    instance_details = self.get_compute_ec2(object_id=self.snapshot_details['snappableId'])
    if not input:
        self.instance_name = instance_details['instanceName']
    self.aws_instance_name = input


def aws_vpc_validation(self, input=None):
    self.aws_vpcs = self._get_aws_region_vpcs(self.aws_region, self.aws_account_map[self.aws_account_number]['id'])
    if not input or input not in self.aws_vpcs:
        raise ValidationException("vpc not found, valid vpcs are {}".format(list(self.aws_vpcs)))
    self.aws_vpc = input


def aws_subnet_validation(self, input=None):
    if not input or input not in self.aws_vpcs[self.aws_vpc]['subnets']:
        raise ValidationException("subnet not found, valid subnets are {}".format(list(self.aws_vpcs[self.aws_vpc]['subnets'])))
    self.aws_subnet = input


def aws_security_group_validation(self, input=None):
    for sg in input:
        if not sg or sg not in self.aws_vpcs[self.aws_vpc]['security_groups']:
            raise ValidationException("security_group not found, valid security_groups are {}".format(list(self.aws_vpcs[self.aws_vpc]['security_groups'])))
    self.aws_security_group = input


def copy_tags_validation(self, input=None):
    if not input:
        input = True
    self.copy_tags = input


def use_replica_validation(self, input=None):
    if not input:
        input = False
    self.use_replica = input

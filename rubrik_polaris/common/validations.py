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

ERROR_MESSAGES = {
    'INVALID_FIRST': "'{}' is an invalid value for 'first'. Value must be an integer greater than 0.",
    'INVALID_BOOLEAN': 'Un-supported boolean type.',
    'REQUIRED_ARGUMENT': '{} field is required.',
    'INVALID_FIELD_TYPE': "'{}' is an invalid value for '{}'. Value must be in {}.",
    'INVALID_INPUT': "{} is an invalid input type. Value must be str or list.",
    'INVALID_NUMBER': "'{}' is an invalid number.",
    'INVALID_ID_FORMAT': "'{}' is an invalid value for '{}'. Please remove leading/trailing spaces."
}


def _validate(self, **kwargs):
    for validation in kwargs:
        if not kwargs[validation]:
            kwargs[validation] = "NONE"
        if isinstance(kwargs[validation], list):
            for test in kwargs[validation]:
                setattr(self, validation, globals()['_' + validation + '_validation'](self, test_variable=test))
        else:
            setattr(self, validation,
                    globals()['_' + validation + '_validation'](self, test_variable=kwargs[validation]))


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
    if not test_variable or test_variable not in self.aws_account_map or self.aws_account_map[test_variable][
        'status'].lower() != 'connected':
        for account in self.aws_account_map:
            if self.aws_account_map[account]['status'].lower() == 'connected':
                connected_accounts.append(account)
        raise ValidationException(
            "{} not found or not connected, valid account numbers are {}".format(test_variable, connected_accounts))
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
        raise ValidationException(
            "{} not found, valid subnets are {}".format(test_variable, list(self.aws_vpcs[self.aws_vpc]['subnets'])))
    return test_variable


def _aws_security_group_validation(self, test_variable=None):
    if not test_variable or test_variable not in self.aws_vpcs[self.aws_vpc]['security_groups']:
        raise ValidationException("{} not found, valid security_groups are {}".format(test_variable, list(
            self.aws_vpcs[self.aws_vpc]['security_groups'])))
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
    try:
        UUID(test_variable)
        return test_variable
    except:
        raise ValidationException("{} not a UUID".format(test_variable))


def _azure_subscription_ids(self, test_variable=None):
    if not test_variable:
        raise ValidationException("No subscription ids in list")
    if not _uuid_validation(test_variable=test_variable):
        raise ValidationException("{} is not a UUID".format(test_variable))
    return test_variable


def _cdm_cluster_id_validation(self, test_variable=None):
    if not test_variable:
        raise ValidationException("cdm_cluster_id not specified: ".format(test_variable))
    if not _uuid_validation((test_variable=test_variable):
        raise ValidationException("{} is not a UUID".format(test_variable))
    return test_variable


def _host_list_validation(self, test_variable=None):
    if not test_variable:
        raise ValidationException("host_list not specified : {}".format(test_variable))
    if isinstance(test_variable, list):
        return test_variable
    hosts = [host.strip() for host in test_variable.split(",")]
    return hosts


def _rbs_port_ranges_validation(self, test_variable=None):
    if not test_variable:
        raise ValidationException("rbs_port_ranges not specified : {}".format(test_variable))

    for k in ['portMin', 'portMax']:
        v = test_variable.get(k)
        if v is None or not isinstance(v, int):
            raise ValidationException("rbs_port_ranges['{}'] must be an int: {}".format(k, test_variable))
    return test_variable


def _kupr_cluster_type_validation(self, test_variable=None):
    test = self.get_enum_values(name="K8sClusterProtoType")
    if not test_variable or test_variable not in test:
        raise ValidationException("{} not found, valid kupr cluster types are {}".format(test_variable, list(test)))
    return test_variable


def _kupr_cluster_id_validation(self, test_variable=None):
    if not UUID(test_variable):
        raise ValidationException("{} not a UUID".format(test_variable))
    return test_variable


def check_first_arg(self, first):
    """Function to validate a common argument named first

    Args:
        first (Any): Number of results to retrieve in the response.

    Returns:
        Optional[int]: An integer value if the 'first' argument is valid

    Raises:
        ValueError: If the 'first' argument contains invalid value
    """
    if first:
        if not isinstance(first, (int, str)) or (isinstance(first, str) and not first.isdigit()):
            raise ValueError(ERROR_MESSAGES['INVALID_NUMBER'].format(first))
        first = int(first)
    if first is not None and first <= 0:
        raise ValueError(ERROR_MESSAGES['INVALID_FIRST'].format(first))

    return first


def to_boolean(self, value):
    """
    Converts value into a boolean type.
    Args:
        value: argument for type casting

    Returns:
        Either True or False

    Raises ValueError
    """
    if isinstance(value, bool):
        return value

    if isinstance(value, str):
        if value.lower() == 'true':
            return True
        elif value.lower() == 'false':
            return False
    raise ValueError(ERROR_MESSAGES['INVALID_BOOLEAN'])


def validate_id(self, id_: str, field_name: str):
    """
    Performs validation for ID
    Args:
        field_name: The field name for which validation is performed.
        id_: ID to validate.

    Returns: return without any error.

    Raises: ValueError exception
    """
    if not id_:
        raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format(field_name))
    elif isinstance(id_, str) and id_.strip() != id_:
        raise ValueError(ERROR_MESSAGES['INVALID_ID_FORMAT'].format(id_, field_name))
    return id_


def check_enum(self, value, field_name, enum_name):
    """
    Verify the value(s) is/are present in the list of enum values

    Args:
        value: Value(s) to verify
        field_name: Name of the field to verify
        enum_name: Name of the enum
    Raises:
        ValueError: If input is invalid
    Returns:
        Optional[list, str]: Verified value(s)
    """
    list_of_enum = self.get_enum_values(name=enum_name)

    if isinstance(value, str):
        if value and value not in list_of_enum:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                value, field_name, list_of_enum))

    elif isinstance(value, list):
        value = [x for x in value if x]
        invalid = [val for val in value if val and val not in list_of_enum]
        if invalid:
            raise ValueError(ERROR_MESSAGES['INVALID_FIELD_TYPE'].format(
                invalid, field_name, list_of_enum))

    elif not value:
        return

    else:
        raise ValueError(ERROR_MESSAGES['INVALID_INPUT'].format(value))
    return value

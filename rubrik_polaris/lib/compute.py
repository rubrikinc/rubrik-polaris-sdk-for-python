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


"""
Collection of functions that manipulate compute components
"""


def get_compute_object_ids_ec2(self, match_all=True, **kwargs):
    """Retrieves all AWS EC2 object IDs that match query

    Arguments:
        match_all {bool} -- Set to false to match ANY defined criteria
        tags {name: value} -- Allows simple qualification of tags
        kwargs {} -- Any top level object from the get_compute_ec2 call

    Returns:
        list -- List of all the EC2 object id's 
    """
    try:
        for instance in self.get_compute_ec2():
            object_ids = []
            num_criteria = len(kwargs)
            if 'tags' in kwargs:
                num_criteria = num_criteria + len(kwargs['tags']) - 1
            num_unmatched_criteria = num_criteria
            for key in kwargs:
                if key == 'tags' and 'tags' in instance:
                    for instance_tag in instance['tags']:
                        if instance_tag['key'] in kwargs['tags'] and \
                                instance_tag['value'] == kwargs['tags'][instance_tag['key']]:
                            num_unmatched_criteria -= 1
                elif key in instance and instance[key] == kwargs[key]:
                    num_unmatched_criteria -= 1
            if match_all and num_unmatched_criteria == 0:
                object_ids.append(instance['id'])
            elif not match_all and num_criteria > num_unmatched_criteria >= 1:
                object_ids.append(instance['id'])
        return object_ids
    except Exception:
        raise


def get_compute_object_ids_azure(self, match_all=True, **kwargs):
    """Retrieves all Azure VM object IDs that match query

    Arguments:
        match_all {bool} -- Set to false to match ANY defined criteria
        kwargs {} -- Any top level object from the get_compute_azure call
    
    Returns:
        list -- List of all the Azure VM object id's 
    """
    try:
        return self._get_compute_object_ids(self.get_compute_azure(), kwargs, match_all=match_all)
    except Exception:
        raise


def get_compute_object_ids_gce(self, match_all=True, **kwargs):
    """Retrieves all GCE object IDs that match query

    Arguments:
        match_all {bool} -- Set to `False` to match ANY defined criteria
        kwargs {} -- Any top level object from the get_compute_gce call
    
    Returns:
        list -- List of all the GCE object id's 
    """
    try:
        return self._get_compute_object_ids(self.get_compute_gce(), kwargs, match_all=match_all)
    except Exception:
        raise


def _get_compute_object_ids_vsphere(self, match_all=True, **kwargs):
    """Retrieves all vSphere objects that match query

    Arguments:
        match_all {bool} -- Set to false to match ANY defined criteria
        kwargs {} -- Any top level object from the get_compute_ec2 call
    """
    try:
        return self._get_object_ids_instances(self.get_instances_vsphere(), kwargs, match_all=match_all)
    except Exception:
        raise


def _get_compute_object_ids(self, instances, criterias, match_all=True):
    try:
        object_ids = []

        for instance in instances:
            num_criteria = len(criterias)
            num_unmatched_criteria = num_criteria

            for key in criterias:
                if key in instance and instance[key] == criterias[key]:
                    num_unmatched_criteria -= 1

            if match_all and num_unmatched_criteria == 0:
                object_ids.append(instance['id'])
            elif not match_all and num_criteria > num_unmatched_criteria >= 1:
                object_ids.append(instance['id'])

        return object_ids
    except Exception:
        raise


def get_compute_ec2(self, object_id=None):
    """Retrieve all AWS EC2 instances from Polaris
    
    Arguments:
        object_id {str} -- A specific Object ID to retrieve

    Returns:
        list -- List of all the AWS EC2 instances or the specific instance if the `object_id` is passed.
    """
    try:
        if object_id:
            query_name = "compute_aws_ec2_detail"
            variables = {
                "object_id": object_id
            }
            return self._query(query_name, variables)
        else:
            query_name = "compute_aws_ec2"
            return self._query(query_name, None)
    except Exception:
        raise


def get_compute_azure(self):
    """Retrieve all Azure instances from Polaris
    
    Returns:
        list -- List of all Azure VM instances
    """
    try:
        query_name = "compute_azure_iaas"
        return self._query(query_name, None)
    except Exception:
        raise


def get_compute_gce(self):
    """Retrieve all GCE instances from Polaris
        
    Returns:
        list -- List of all GCE instances
    """
    try:
        query_name = "compute_gcp_gce"
        return self._query(query_name, None)
    except Exception:
        raise


def get_compute_vsphere(self):
    """ Retrieve all vSphere instances from Polaris """
    try:
        query_name = "compute_vmware_vsphere"
        variables = {"filter": []}
        return self._query(query_name, variables)
    except Exception:
        raise


def _submit_compute_restore(self, snapshot_id, **kwargs):
    """Submits a Restore of a compute instance

    Arguments:
        query_name {string} -- Backend query name for operation
        snapshot_id {string} -- Snapshot ID to be restored
        should_power_on {bool} -- Defaults to False
        should_restore_tags {bool} -- Defaults to False
        wait {bool} -- Return once complete Defaults to False
    """

    should_power_on = False
    if kwargs and 'should_power_on' in kwargs and kwargs['should_power_on']:
        should_power_on = True

    should_restore_tags = False
    if kwargs and 'should_restore_tags' in kwargs and kwargs['should_restore_tags']:
        should_restore_tags = True

    try:
        mutation_name = kwargs['mutation']
        variables = {
            "snapshot_id": snapshot_id,
            "should_power_on": should_power_on,
            "should_restore_tags": should_restore_tags
        }

        if mutation_name not in self._graphql_query:
            raise Exception("Mutation not found : {}".format(mutation_name))

        result = self._query(mutation_name, variables)
        if 'errors' in result and result['errors']:
            return {'errors': result['errors'][0]['message']}

        results = []
        if 'wait' in kwargs:
            results = self._monitor_task(result)

        return results
        # TODO: find a better way to report errors per uuid
    except Exception:
        raise


def submit_compute_restore_ec2(self, snapshot_id, **kwargs):
    """Submits a Restore of an EC2 instance

    Arguments:
        snapshot_id {str} -- Snapshot ID to be restored
        should_power_on {bool} -- Defaults to `False`
        should_restore_tags {bool} -- Defaults to `False`
        wait {bool} -- Return once complete Defaults to `False`
    
    Returns:
        list -- List of errors if any occurred during the restore
    """
    return self._submit_compute_restore(snapshot_id, mutation="compute_restore_ec2", **kwargs)


def submit_compute_restore_azure(self, snapshot_id, **kwargs):
    """Submits a Restore of an Azure VM instance

    Arguments:
        snapshot_id {str} -- Snapshot ID to be restored
        should_power_on {bool} -- Defaults to `False`
        should_restore_tags {bool} -- Defaults to `False`
        wait {bool} -- Return once complete Defaults to `False`

    Returns:
        list -- List of errors if any occurred during the restore
    """
    return self._submit_compute_restore(snapshot_id, mutation="compute_restore_azure", **kwargs)


def submit_compute_restore_gce(self, snapshot_id, **kwargs):
    """Submits a Restore of a GCE instance

    Arguments:
        snapshot_id {str} -- Snapshot ID to be restored
        should_power_on {bool} -- Defaults to `False`
        should_restore_tags {bool} -- Defaults to `False`
        wait {bool} -- Return once complete Defaults to `False`

    Returns:
        list -- List of errors if any occurred during the restore
    """
    return self._submit_compute_restore(snapshot_id, mutation="compute_restore_gce", **kwargs)


def _get_aws_region_kmskeys(self, region, aws_native_account_id):
    try:
        query_name = "compute_aws_region_kmskeys"
        variables = {"region": region, "aws_native_account_id": aws_native_account_id}
        return self._query(query_name, variables)
    except Exception:
        raise


def _get_aws_region_sshkeypairs(self, region, aws_native_account_id):
    try:
        query_name = "compute_aws_region_sshkeypairs"
        variables = {"region": region, "aws_native_account_id": aws_native_account_id}
        return self._query(query_name, variables)
    except Exception:
        raise


def _get_aws_region_vpcs(self, region, aws_native_account_id):
    try:
        output = {}
        query_name = "compute_aws_region_vpcs"
        variables = {"region": region, "aws_native_account_id": aws_native_account_id}
        vpcs = self._query(query_name, variables)
        for vpc in vpcs:
            output[vpc['id']] = {}
            output[vpc['id']]['vpc_name'] = vpc['name']
            output[vpc['id']]['security_groups'] = {}
            for sg in vpc['securityGroups']:
                output[vpc['id']]['security_groups'][sg['id']] = {}
                output[vpc['id']]['security_groups'][sg['id']]['sg_name'] = sg['name']
            output[vpc['id']]['subnets'] = {}
            for sn in vpc['subnets']:
                output[vpc['id']]['subnets'][sn['id']] = {}
                output[vpc['id']]['subnets'][sn['id']]['name'] = sn['name']
                output[vpc['id']]['subnets'][sn['id']]['availability_zone'] = sn['availabilityZone']
        return output
    except Exception:
        raise


def submit_compute_export_ec2(self, snapshot_id=None, account_number=None, region=None, vpc=None,
                              security_groups=None, subnet=None, wait=False, instance_type=None, instance_name=None, **kwargs):
    """ Submits the export of a EC2 instance"""
    from rubrik_polaris.exceptions import ValidationException

    if not snapshot_id:
        print("no snapshot_id specified")
        return

    try:
        snapshot_details = self._get_snapshot(snapshot_id=snapshot_id)
        if snapshot_details['isCorrupted']:
            raise ValidationException("snapshot_id appears to be corrupted : {}".format(snapshot_id))
        if snapshot_details['isDeletedFromSource']:
            raise ValidationException("snapshot_id has been deleted from the source : {}".format(snapshot_id))
        if snapshot_details['isExpired']:
            raise ValidationException("snapshot_id is expired : {}".format(snapshot_id))
    except Exception:
        raise ValidationException("not a valid snapshot_id : {}".format(snapshot_id))

    instance_details = self.get_compute_ec2(object_id=snapshot_details['snappableId'])
    account_map = self._get_account_map_aws()
    connected_accounts = []

    if not account_number or account_number not in account_map or account_map[account_number]['status'].lower() != 'connected':
        for account in account_map:
            if account_map[account]['status'].lower() == 'connected':
                connected_accounts.append(account)
        raise ValidationException("account_number not found or not connected, valid account numbers are {}".format(connected_accounts))
        return

    regions = self.get_enum_values(name="AwsNativeRegionEnum")
    if not region or region not in regions:
        raise ValidationException("region not found, valid regions are {}".format(list(regions)))
        return

    instance_types = self.get_enum_values(name="AwsNativeEc2InstanceTypeEnum")
    if not instance_type or instance_type not in instance_types:
        instance_type = instance_details['instanceType']

    if not instance_name:
        instance_name = instance_details['instanceName']

    vpcs = self._get_aws_region_vpcs(region, account_map[account_number]['id'])
    if not vpc or vpc not in vpcs:
        raise ValidationException("vpc not found, valid vpcs are {}".format(list(vpcs)))
        return

    for sg in security_groups:
        if not sg or sg not in vpcs[vpc]['security_groups']:
            raise ValidationException("security_group not found, valid security_groups are {}".format(list(vpcs[vpc]['security_groups'])))
            return

    if not subnet or subnet not in vpcs[vpc]['subnets']:
        raise ValidationException("subnet not found, valid subnets are {}".format(list(vpcs[vpc]['subnets'])))
        return

    if 'copy_tags' not in kwargs:
        copy_tags = True

    if 'use_replica' not in kwargs:
        use_replica = False

    variables = {
        "snapshot_id": snapshot_id,
        "account_id": account_map[account_number]['id'],
        "security_group_ids": security_groups,
        "subnet_id": subnet,
        "region": region,
        "instance_name": instance_name,
        "instance_type": instance_type,
        "copy_tags": copy_tags,
        "use_replica": use_replica
        # Will need validations for these when requests come in.
        # "ssh_keypair_name":
        # "kms_key_id":
    }

    result = _submit_compute_export(self, mutation_name='compute_export_ec2', variables=variables, wait=wait)
    return result


def _submit_compute_export(self, mutation_name=None, variables=None, wait=False):
    try:

        if mutation_name not in self._graphql_query_map:
            raise Exception("Mutation not found : {}".format(mutation_name))

        result = self._query(mutation_name, variables)
        if 'errors' in result and result['errors']:
            return {'errors': result['errors'][0]['message']}

        results = []
        if wait:
            results = self._monitor_task(result)

        return results
    except Exception:
        raise

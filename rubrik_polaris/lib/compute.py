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
            self._validate(
                query_name=query_name
            )
            variables = {
                "object_id": object_id
            }
            return self._query(self.query_name, variables)
        else:
            query_name = "compute_aws_ec2"
            self._validate(
                query_name=query_name
            )
            return self._query(self.query_name, None)
    except Exception:
        raise


def get_compute_azure(self):
    """Retrieve all Azure instances from Polaris
    
    Returns:
        list -- List of all Azure VM instances
    """
    try:
        query_name = "compute_azure_iaas"
        self._validate(
            query_name=query_name
        )
        return self._query(self.query_name, None)
    except Exception:
        raise


def get_compute_gce(self):
    """Retrieve all GCE instances from Polaris
        
    Returns:
        list -- List of all GCE instances
    """
    try:
        query_name = "compute_gcp_gce"
        self._validate(
            query_name=query_name
        )
        return self._query(self.query_name, None)
    except Exception:
        raise


def get_compute_vsphere(self):
    """ Retrieve all vSphere instances from Polaris """
    from rubrik_polaris.exceptions import RequestException
    try:
        query_name = "compute_vmware_vsphere"
        # self._validate(
        #     query_name=query_name
        # )
        variables = {"filter": [], "first": 500}
        return self._query(query_name, variables)
    except Exception:
        raise


def _submit_compute_restore(self, snapshot_id=None, mutation_name=None,  should_power_on=True, should_restore_tags=True, **kwargs):
    """Submits a Restore of a compute instance

    Arguments:
        query_name {string} -- Backend query name for operation
        snapshot_id {string} -- Snapshot ID to be restored
        should_power_on {bool} -- Defaults to False
        should_restore_tags {bool} -- Defaults to False
        wait {bool} -- Return once complete Defaults to False
    """

    self._validate(
        snapshot_id=snapshot_id,
        mutation_name=mutation_name
    )

    try:
        variables = {
            "snapshot_id": snapshot_id,
            "should_power_on": should_power_on,
            "should_restore_tags": should_restore_tags
        }

        result = self._query(self.mutation_name, variables)
        if 'errors' in result and result['errors']:
            return {'errors': result['errors'][0]['message']}

        results = []
        if 'wait' in kwargs:
            results = self._monitor_task(result)

        return results
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
    return self._submit_compute_restore(snapshot_id=snapshot_id, mutation="compute_restore_ec2", **kwargs)


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
    return self._submit_compute_restore(snapshot_id=snapshot_id, mutation_name="compute_restore_azure", **kwargs)


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
    return self._submit_compute_restore(snapshot_id=snapshot_id, mutation_name="compute_restore_gce")


def _get_aws_region_kmskeys(self, aws_region, aws_native_account_id):
    try:
        query_name = "compute_aws_region_kmskeys"
        self._validate(
            query_name=query_name,
            aws_region=aws_region
        )
        variables = {"region": aws_region, "aws_native_account_id": aws_native_account_id}
        return self._query(self.query_name, variables)
    except Exception:
        raise


def _get_aws_region_sshkeypairs(self, aws_region=None, aws_native_account_id=None):
    try:
        query_name = "compute_aws_region_sshkeypairs"
        self._validate(
            query_name=query_name,
            aws_region=aws_region
        )
        variables = {
            "region": self.aws_region,
            "aws_native_account_id": self.aws_native_account_id
        }
        return self._query(self.query_name, variables)
    except Exception:
        raise


def _get_aws_region_vpcs(self, aws_region, aws_native_account_id):
    try:
        output = {}
        query_name = "compute_aws_region_vpcs"
        self._validate(
            query_name=query_name,
            aws_native_account_id=aws_native_account_id,
            aws_region=aws_region
        )
        variables = {"region": aws_region, "aws_native_account_id": aws_native_account_id}
        vpcs = self._query(self.query_name, variables)
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


def submit_compute_export_ec2(self, snapshot_id=None, aws_account_number=None, aws_region=None, aws_vpc=None,
                              aws_security_groups=None, aws_subnet=None, wait=False, aws_instance_type=None, aws_instance_name=None, copy_tags=True, use_replica=False):
    """ Submits the export of a EC2 instance"""
    from rubrik_polaris.exceptions import ValidationException

    mutation_name = 'compute_export_ec2'
    self._validate(
        mutation_name=mutation_name,
        aws_account_number=aws_account_number,
        aws_region=aws_region,
        aws_vpc=aws_vpc,
        aws_subnet=aws_subnet,
        aws_security_group=aws_security_groups,
        snapshot_id=snapshot_id,
        aws_instance_name=aws_instance_name,
        aws_instance_type=aws_instance_type,
        copy_tags=copy_tags,
        use_replica=use_replica
    )

    variables = {
        "snapshot_id": self.snapshot_id,
        "account_id": self.aws_account_map[aws_account_number]['id'],
        "security_group_ids": self.aws_security_groups,
        "subnet_id": self.aws_subnet,
        "region": self.aws_region,
        "instance_name": self.aws_instance_name,
        "instance_type": self.aws_instance_type,
        "copy_tags": self.copy_tags,
        "use_replica": self.use_replica
        # Will need validations for these when requests come in.
        # "ssh_keypair_name":
        # "kms_key_id":
    }

    result = _submit_compute_export(self, mutation_name=self.mutation_name, variables=variables, wait=wait)
    return result


def _submit_compute_export(self, mutation_name=None, variables=None, wait=False):
    try:

        self._validate(
            mutation_name=mutation_name
        )
        result = self._query(self.mutation_name, variables)
        if 'errors' in result and result['errors']:
            return {'errors': result['errors'][0]['message']}
        results = []
        if wait:
            results = self._monitor_task(result)
        return results
    except Exception:
        raise

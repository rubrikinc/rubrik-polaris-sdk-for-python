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
Collection of functions that manipulate GCE compute components
"""


def get_compute_object_ids_gce(self, match_all=True, **kwargs):
    """Retrieves all GCP GCE object IDs that match query

    Args:
        match_all (bool): Set to false to match ANY defined criteria
        kwargs (str): Any top level object from the get_compute_gce call

    Returns:
        list: List of all the GCE object id's

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        return self._get_compute_object_ids(self.get_compute_gce(), kwargs, match_all=match_all)
    except Exception:
        raise


def get_compute_gce(self):
    """Retrieves all GCP GCE object details

    Returns:
        dict: details of GCP GCE objects

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "compute_gcp_gce"
        self._validate(
            query_name=query_name
        )
        return self._query(self.query_name, None)
    except Exception:
        raise


def submit_compute_restore_gce(self, snapshot_id, **kwargs):
    """Submits a Restore of a GCE instance

    Args:
        snapshot_id (str): Snapshot ID to be restored
        should_power_on (bool): Defaults to `False`
        should_restore_tags (bool): Defaults to `False`
        wait (bool): Return once complete Defaults to `False`

    Returns:
        dict -- List of errors if any occurred during the restore
    """
    return self._submit_compute_restore(snapshot_id=snapshot_id, mutation_name="compute_restore_gce")


def submit_compute_export_gce(self, snapshot_id=None, instance_name=None, machine_type=None, network_tags=None,
                              subnet_name=None, zone=None, copy_labels=None, add_rubrik_labels=None, project_id=None,
                              power_off=None, disk_encryption_type=None, kms_key=None, kms_key_id=None, wait=False):
    """ Submits the export of a GCE instance"""

    mutation_name = 'compute_export_gce'

    self._validate(
        mutation_name=mutation_name,
        snapshot_id=snapshot_id
    )

    variables = {
        "snapshot_id": snapshot_id, #UUID! - done
        "instance_name": instance_name,
        "machine_type": machine_type, #String!
        "network_tags": network_tags, #[String!],
        "subnet_name": subnet_name, #String!,
        "zone": zone, #String!,
        "copy_labels": copy_labels, #Boolean!,
        "add_rubrik_labels": add_rubrik_labels, #Boolean!,
        "project_id": project_id, #String!,
        "power_off": power_off, #Boolean!,
        "disk_encryption_type": disk_encryption_type, #DiskEncryptionType!,
        "kms_key": kms_key, #kmsCryptoKey,
        "kms_key_id": kms_key_id #String
    }

    result = self._submit_compute_export(self, mutation_name=self.mutation_name, variables=variables, wait=wait)
    return result
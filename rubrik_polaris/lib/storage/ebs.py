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
Collection of functions that manipulate storage components.
"""


def get_storage_object_ids_ebs(self, match_all=True, **kwargs):
    """Retrieves ObjectIds for EBS Snappables from Polaris

    Args:
        match_all (bool): Set to False to match ANY defined criteria
        tags (dict): Optional allows simple qualification of tags
        kwargs (dict): Optional any top level object from the get_storage_ebs call

    Returns:
        list: A list of EBS object IDs matching results of query

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> snappables = client.get_object_ids_ebs(tags={"Environment": "staging"})
        >>> for snappable in snappables:
        ...    snapshot = client.get_snapshots(snappable, recovery_point='latest')
        ...    if snapshot:
        ...        print(snapshot[0])
    """

    try:
        object_ids = []

        for volume in self.get_storage_ebs():
            num_criteria = len(kwargs)
            if 'tags' in kwargs:
                num_criteria = num_criteria + len(kwargs['tags']) - 1
            num_unmatched_criteria = num_criteria

            for key in kwargs:
                if key == 'tags' and 'tags' in volume:
                    for volume_tag in volume['tags']:
                        if volume_tag['key'] in kwargs['tags'] and \
                           volume_tag['value'] == kwargs['tags'][volume_tag['key']]:
                            num_unmatched_criteria -= 1
                elif key in volume and volume[key] == kwargs[key]:
                    num_unmatched_criteria -= 1
            if match_all and num_unmatched_criteria == 0:
                object_ids.append(volume['id'])
            elif not match_all and num_criteria > num_unmatched_criteria >= 1:
                object_ids.append(volume['id'])
        return object_ids
    except Exception:
        raise


def get_storage_ebs(self):
    """Retrieves details for all EBS Snappables from Polaris

    Args:

    Returns:
        dict: Dictionary of all EBS Snappable details

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> snappables = client.get_storage_ebs()
    """
    try:
        query_name = "storage_aws_ebs"
        return self._query(query_name, None)
    except Exception:
        raise

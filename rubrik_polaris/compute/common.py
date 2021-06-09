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

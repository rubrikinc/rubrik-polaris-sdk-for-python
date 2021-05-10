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
Collection of functions that manipulate appflows components
"""

def get_appflows_blueprints(self, blueprint_name=""):
    """Retrieves dictionary of AppFlows blueprints including identifiers and additional details.

    Keyword Arguments:
        blueprint_name {str} -- Rubrik AppFlows blueprint name (default: {''})

    Returns:
        dict -- A single AppFlows blueprint dict if a non-empty `blueprint_name` is given and found.
        list -- The complete set of AppFlows blueprints in a list of dictionaries.
    """
    from rubrik_polaris.exceptions import RequestException

    try:
        query_name = "appflows_blueprints_list"
        variables = {
            "filter": [
                {
                    "field": "NAME",
                    "texts": [
                        blueprint_name
                    ]
                }
            ]
        }
        request = self._query(query_name, variables)
        request_nodes = self._dump_nodes(request)
        if blueprint_name:
            for node in request_nodes:
                if node['name'] == blueprint_name:
                    return node
        return request_nodes
    except Exception:
        raise

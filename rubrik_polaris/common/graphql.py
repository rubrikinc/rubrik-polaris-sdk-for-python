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
Collection of methods that interact with the raw GraphQL.
"""

import re
import sys

def _build_graphql_maps(self):
    from os import listdir
    from os.path import isfile, join

    # Assemble GraphQL query/mutation hash and name map
    graphql_details = {}

    file_query_prefix = 'query'
    file_mutation_prefix = 'mutation'
    file_suffix = '.graphql'

    try:
        graphql_files = [f for f in listdir(self._data_path)
                     if isfile(join(self._data_path, f)) and f.endswith(file_suffix)]
    except:
        print("Unexpected error:", sys.exc_info()[0])
        raise

    for f in graphql_files:
        query_name = f.replace(file_suffix, '')
        if f.startswith(file_query_prefix):
            query_name = query_name.replace('{}_'.format(file_query_prefix), '')
        elif f.startswith(file_mutation_prefix):
            query_name = query_name.replace('{}_'.format(file_mutation_prefix), '')

        try:
            graphql_file = open("{}{}".format(self._data_path, f), 'r').read()
            graphql_details[query_name] = self._get_details_from_graphql_query(graphql_file)
            op_name = "SdkPython" + ''.join(w[:1].upper() + w[1:] for w in query_name.split('_'))
            graphql_details[query_name]['operation_name'] = op_name
            query_text = """{}""".format(graphql_file)
            query_text = re.sub("RubrikPolarisSDKRequest", op_name, query_text)
            graphql_details[query_name]['query_text'] = query_text

        except OSError as e:
            raise  # TODO: Should we bail immediately or go on to the next file?

    return graphql_details


def _get_details_from_graphql_query(self, graphql_query_text):
    import sys
    try:
        o = {}
        try:
            o['gql_name'] = re.findall(r' +(\S+) ?\(.*', graphql_query_text)[1]
            paren = re.search(r'\((.*?)\)', graphql_query_text).group(1).split(',')
            for i in paren:
                item = re.search(r'^(.*):(.*$)', i)
                var_name = item.group(1).strip()
                o[var_name] = {}
                if '=' in item.group(2):
                    default_split = item.group(2).split('=')
                    o[var_name]['default'] = default_split[1].strip()
                    o[var_name]['type'] = default_split[0].strip()
                else:
                    o[var_name]['default'] = None
                    o[var_name]['type'] = item.group(2).strip()
                if '[' in o[var_name]['type']:
                    o[var_name]['type'] = re.search(r'\[(.*)\]', o[var_name]['type']).group(1)
                    o[var_name]['typeOf'] = 'arrayOf'
                else:
                    o[var_name]['typeOf'] = 'stringOf'
                if '!' in o[var_name]['type']:
                    o[var_name]['required'] = True
                    o[var_name]['type'] = o[var_name]['type'].replace("!", "")
                else:
                    o[var_name]['required'] = False
        except:  # Handle non-variable queries
            o['gql_name'] = re.sub(r"[\{|\}]", "", re.search(r'\{(.*)\}', re.sub(r"[\n\t\s]*", "", graphql_query_text)).group(0))
        return o
    except:
        print("Unexpected error:", sys.exc_info()[0])
        print(graphql_query_text)
        raise


def _dump_nodes(self, request):
    nodes = []
    if 'data' in request and request['data'] and len(request['data']) > 0:
        query_result = list(request['data'].values())[0]
        if query_result is None:
            return nodes

        if isinstance(query_result, bool):
            return query_result
        if 'states' in query_result:
            for state in query_result['states']:
                nodes.append(state['name'])
        elif 'edges' in query_result:
            for edge in query_result['edges']:
                nodes.append(edge['node'])
        else:
            return query_result
    else:
        return request
    return nodes


def get_enum_values(self, name=None):
    """ Retrieve Enum Values via Introspection """
    try:
        query_name = "graphql_enum_values"
        variables = {"enum_name": name}
        return self._query(query_name, variables)
    except Exception:
        raise

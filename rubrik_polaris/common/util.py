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
Collection of utility methods.
"""

ERROR_MESSAGES = {
    'INVALID_NUMBER': "'{}' is not a valid number",
    'INVALID_FIRST': "'{}' is an invalid value for 'first'. Value must be an integer greater than 0.",
    'INVALID_BOOLEAN': 'Un-supported boolean type.',
    'REQUIRED_ARGUMENT': '{} field is required.'
}


def to_number(self, arg):
    """Converts an argument to a Python int

    Args:
        arg (Any): argument to convert

    Returns:
        Optional[int]: An integer value if the argument can be converted

    Raises:
        ValueError: If the argument can not be converted to Python int
    """
    if arg is None or arg == '':
        return None

    if isinstance(arg, int):
        return arg

    if isinstance(arg, str):
        try:
            return int(float(arg))
        except Exception:
            raise ValueError(ERROR_MESSAGES['INVALID_NUMBER'].format(arg))

    raise ValueError(ERROR_MESSAGES['INVALID_NUMBER'].format(arg))


def check_first_arg(self, first):
    """Function to validate a common argument named first

    Args:
        first (Any): Number of results to retrieve in the response.

    Returns:
        Optional[int]: An integer value if the 'first' argument is valid

    Raises:
        ValueError: If the 'first' argument contains invalid value
    """
    first = to_number(self, first)
    if isinstance(first, int) and first <= 0:
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
        else:
            raise ValueError(ERROR_MESSAGES['INVALID_BOOLEAN'])
    else:
        raise ValueError(ERROR_MESSAGES['INVALID_BOOLEAN'].format(value))


def validate_id(self, id_: str, field_name: str):
    """
    Performs validation for ID
    Args:
        field_name: The field name for which validation is performed.
        id_: ID to validate.

    Returns: return without any error.

    Raises: ValueError exception
    """
    if isinstance(id_, str):
        id_ = id_.strip()

    if not id_:
        raise ValueError(ERROR_MESSAGES['REQUIRED_ARGUMENT'].format(field_name))

    return id_

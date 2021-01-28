#!/usr/bin/env python3
from glob import glob

import setuptools

long_description = """
# Rubrik SDK for Polaris

This project provides a Python package that makes it easy to interact with the Rubrik Polaris API.

The SDK has been tested against Python 3.6.4.

## Installation

Install from pip:

`Pending`

Install from source:
```
$ git clone https://github.com/rubrikinc/rubrik-polaris-sdk-for-python
$ cd rubrik-polaris-sdk-for-python
$ git checkout beta
$ python setup.py install
```
## Quick Start

## Documentation

## Example

## Additional Links
"""


setuptools.setup(
    name="rubrik_polaris",
    version="21.01.08",
    author="Rubrik Inc",
    description="A Python package for interacting with the Rubrik Polaris API.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/rubrikinc/rubrik-polaris-sdk-for-python",
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        "Intended Audience :: Information Technology",
        "Intended Audience :: System Administrators",
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 3.6"
    ],
    install_requires=[
        'requests >= 2.23.0',
        'python-dateutil',
        'pytz',
        'zulu',
        'boto3',
        'botocore<1.20.0,>=1.19.59',
        'google-api-python-client',
        'oauth2client',
        'httplib2 <1dev, >=0.15.0'
    ],
    include_package_data=True,
    data_files = [
        ('rubrik_polaris/graphql', glob('rubrik_polaris/lib/common/graphql/*'))
    ],
    tests_require=[
        'pytest'
    ],
    zip_safe=False,
)

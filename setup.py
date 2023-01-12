#!/usr/bin/env python3
from datetime import datetime
from glob import glob

import setuptools


name = 'Rubrik Polaris SDK for Python'
version = '2023.01.12'
release = '2023.01.12-beta'
author = 'Rubrik Inc'
license = 'MIT'
copyright = '{}, {}'.format(datetime.now().year, author)


# read the contents of your README file
from os import path
this_directory = path.abspath(path.dirname(__file__))
with open(path.join(this_directory, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()


setuptools.setup(
    name=name,
    version=version,
    author=author,
    license=license,
    description='A Python package for interacting with the Rubrik Polaris API.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    url='https://github.com/rubrikinc/rubrik-polaris-sdk-for-python',
    keywords='rubrik polaris cdm api',
    packages=setuptools.find_packages(exclude=['tests']),
    classifiers=[
        'Intended Audience :: Information Technology',
        'Intended Audience :: System Administrators',
        'License :: OSI Approved :: Apache Software License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.8'
    ],
    install_requires=[
        'requests >= 2.23.0',
        'python-dateutil',
        'pytz',
        'zulu',
        'boto3',
        'botocore',
        'google-auth<3.0dev,>=2.14.1',
        'google-api-python-client',
        'oauth2client',
        'six>=1.13.0',
        'pyasn1<0.5.0,>=0.4.6',
        'httplib2 <1dev, >=0.15.0'
    ],
    include_package_data=True,
    data_files = [
        ('rubrik_polaris/graphql', glob('rubrik_polaris/common/graphql/*'))
    ],
    tests_require=[
        'pytest'
    ],
    zip_safe=False,
    command_options={
        'build_sphinx': {
            'project': ('setup.py', name),
            'version': ('setup.py', version),
            'release': ('setup.py', release),
            'copyright': ('setup.py', copyright)
        }
    },
)

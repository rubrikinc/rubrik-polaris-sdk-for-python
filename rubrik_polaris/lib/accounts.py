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

from rubrik_polaris.exceptions import PolarisException

"""
Collection of functions that manipulate account components.
"""


def add_account_aws(self, aws_regions=[], all=False, aws_profiles=[], aws_access_key_id=None, aws_secret_access_key=None, cloud_account_features=None):
    """Add AWS account to Polaris

    Args:
        aws_regions (list): List of AWS regions to include in Polaris for imported accounts
        aws_profiles (list): Optional list of local profile names to add to Polaris
        all (bool): Optional set true to import all locally configured profiles to Polaris
        aws_access_key_id (str): AWS Access key of account to import to Polaris
        aws_secret_access_key (str): AWS secret of key of account to import to polaris
        cloud_account_features (list): List of services to enable for cloud account

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.add_account_aws(aws_regions = ["us-east-1"], profiles = ["milanese"], cloud_account_features = ["CLOUD_NATIVE_PROTECTION"])
        >>> rubrik.add_account_aws(aws_regions = ["us-east-1"], aws_access_key_id='blah', aws_secret_access_key='blah', cloud_account_features = ["CLOUD_NATIVE_PROTECTION"])
        >>> rubrik.add_account_aws(aws_regions = ["us-west-2"], all = True , cloud_account_features = ["CLOUD_NATIVE_PROTECTION"])

    """
    if aws_access_key_id and aws_secret_access_key:
        self._add_account_aws(aws_regions=aws_regions, aws_id=aws_access_key_id, aws_secret=aws_secret_access_key, cloud_account_features=cloud_account_features)
    elif all or aws_profiles:
        for profile in self._get_aws_profiles():
            if profile in aws_profiles or (all and profile != 'default'):
                self._add_account_aws(profile=profile, aws_regions=aws_regions, cloud_account_features=cloud_account_features)
                #TODO: Should add above into a queque for threaded provisioning


def _add_account_aws(self, aws_regions=[], cloud_account_features=None, profile='', aws_id=None, aws_secret=None):
    aws_account_id = None
    aws_account_name = None

    if profile:
        aws_account_id, aws_account_name = self.get_account_aws_native_id(profile=profile)
    elif aws_id and aws_secret:
        aws_account_id, aws_account_name = self.get_account_aws_native_id(aws_id=aws_id, aws_secret=aws_secret)

    account_name_list = []
    if aws_account_id:
        account_name_list.append(aws_account_id)
    else:
        return # TODO: Raise error message in return stack (FDSE-848)

    if aws_account_name:
        account_name_list.append(aws_account_name)
    if profile:
        account_name_list.append(profile)

    try:
        account_initiate_result = _add_account_aws_initiate(self, cloud_account_features=cloud_account_features, account_name_list=account_name_list, aws_account_id=aws_account_id)['initiateResponse']
        account_commit_result = _add_account_aws_commit(self, cloud_account_features=cloud_account_features, account_name_list=account_name_list, aws_account_id=aws_account_id, account_initiate_result=account_initiate_result, aws_regions=aws_regions)
    except Exception:
        raise

    else:
        if profile:
            _invoke_aws_stack(self, account_initiate_result=account_initiate_result, aws_account_id=aws_account_id, regions=aws_regions, profile=profile)
        elif aws_id and aws_secret:
            _invoke_aws_stack(self, account_initiate_result=account_initiate_result, aws_account_id=aws_account_id, regions=aws_regions, aws_id=aws_id, aws_secret=aws_secret)


def _add_account_aws_commit(self, aws_regions=None, cloud_account_features=None, account_name_list=None, aws_account_id=None, account_initiate_result=None):
    cloud_account_action = 'CREATE'
    cloud_account_features = cloud_account_features
    query_name = "accounts_aws_add_commit"
    self._validate(
        cloud_account_action=cloud_account_action,
        query_name=query_name,
        cloud_account_features=cloud_account_features,
        aws_regions=aws_regions
    )
    variables = {
        "aws_account_id": aws_account_id,
        "aws_account_name": " : ".join(account_name_list),
        "aws_regions": aws_regions,
        "external_id": account_initiate_result['externalId'],
        "feature_versions": account_initiate_result['featureVersionList'],
        "stack_name": account_initiate_result['stackName'],
        "cloud_account_action": self.cloud_account_action,
        "cloud_account_features": self.cloud_account_features
    }
    result = self._query(self.query_name, variables)
    if 'errorMessage' in result and result['errorMessage']:
        raise Exception("Account {} already added: {}".format(aws_account_id, result['errorMessage']))
    return result


def _add_account_aws_initiate(self, cloud_account_features=None, account_name_list=None, aws_account_id=None ):
    cloud_account_action = 'CREATE'
    cloud_account_features = cloud_account_features
    query_name = "accounts_aws_add_initiate"
    self._validate(
        cloud_account_action=cloud_account_action,
        query_name=query_name,
        cloud_account_features=cloud_account_features
    )
    variables = {
        "aws_account_id": aws_account_id,
        "account_name": " : ".join(account_name_list),
        "cloud_account_action": self.cloud_account_action,
        "cloud_account_features": self.cloud_account_features
    }
    result = self._query(self.query_name, variables)
    if 'errorMessage' in result and result['errorMessage']:
        raise Exception("Account {} already added: {}".format(aws_account_id, result['errorMessage']))
    return result


def _get_aws_profiles(self):
    import boto3
    return boto3.session.Session().available_profiles


def _invoke_aws_stack(self, account_initiate_result=None, aws_account_id=None, regions=[], profile='', aws_id=None, aws_secret=None):
    import boto3 as boto3
    import re
    from botocore.exceptions import WaiterError

    region = re.sub(r"_", "-", regions[0].lower())
    if profile:
        boto3.setup_default_session(profile_name=profile)
    elif aws_id and aws_secret:
        boto3.setup_default_session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)

    boto_account_id = boto3.client('sts').get_caller_identity().get('Account')
    client = boto3.client('cloudformation', region_name=region)

    if boto_account_id != aws_account_id:
        raise Exception("Account mismatch. Are you using the proper AWS_PROFILE?")

    # Add ability to use local keys
    try:
        create_stack = client.create_stack(
            StackName=account_initiate_result['stackName'],
            TemplateURL=account_initiate_result['templateUrl'],
            DisableRollback=False,
            Capabilities=['CAPABILITY_IAM'],
            EnableTerminationProtection=False
        )
    except Exception as e:
        raise Exception('Stack creation failed with error:\n {}'.format(str(e)))

    waiter = client.get_waiter('stack_create_complete')
    try:
        waiter.wait(StackName=create_stack['StackId'])
    except WaiterError:
        raise


def get_accounts_aws(self, filter=""):
    """Retrieves AWS account information from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of AWS accounts in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_aws"
        variables = {
            "filter": filter
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def get_accounts_gcp(self, filter=""):
    """Retrieves GCP project information from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of GCP Projects in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_gcp"
        variables = {
            "filter": filter
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def get_accounts_azure(self, filter=""):
    """Retrieves Azure account information from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of Azure accounts in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_azure"
        variables = {
            "filter": filter
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def get_accounts_aws_detail(self, filter):
    """Retrieves deployment details for AWS from Polaris

    Args:
        filter (str): Search string to filter results

    Returns:
        dict: Details of Azure accounts in Polaris

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    try:
        query_name = "accounts_aws_detail"
        variables = {
            "filter": filter
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def get_account_aws_native_id(self, profile='', aws_id=None, aws_secret=None):
    """Retrieves AWS Account ID from local config
    
    Args:
        profile (str): Profile name of local configuration
        aws_access_key_id (str): AWS Access key to import to Polaris
        aws_secret_access_key (str): AWS secret of key to import to polaris

    Returns:
        list: AWS account name and ID of requested account

    Raises:
        RequestException: If the query to Polaris returned an error
    """
    import boto3 as boto3
    from botocore.exceptions import ClientError

    try:
        if profile:
            boto3.setup_default_session(profile_name=profile)
        elif aws_id and aws_secret:
            boto3.setup_default_session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)
        try:
            boto_account_id = boto3.client('sts').get_caller_identity().get('Account')
        except ClientError as e:
            print("Boto Error: {}".format(e))
        boto_account_name = None
        try:
            boto_account_name = boto3.client('organizations').describe_account(AccountId=boto_account_id).get('Account').get('Name')
        except ClientError as e:
            if e.response['Error']['Code'] == 'AWSOrganizationsNotInUseException':
                pass
            else:
                raise PolarisException("Unexpected error: %s" % e)
        return boto_account_id, boto_account_name
    except PolarisException:
        raise


def _disable_account_aws(self, polaris_account_id):
    """Disables AWS Account in Polaris

    Arguments:
        polaris_account_id {str} -- Account ID to disable in Polaris
    """
    try:
        query_name = "accounts_aws_disable"
        variables = {
            "polaris_account_id": polaris_account_id
        }
        result = self._query(query_name, variables)
        monitor = self._monitor_task(result)
        if monitor['status'] != 'SUCCEEDED':
            raise Exception("Failed to disable account")
    except Exception:
        raise


def _invoke_account_delete_aws(self, cloud_account_uuid):
    """Invokes initiation of Delete AWS Account in Polaris

    Arguments:
        polaris_account_id {str} -- Account ID to initiate delete in Polaris
    """
    try:
        query_name = "accounts_aws_delete_initiate"
        variables = {
            "cloud_account_uuid": cloud_account_uuid
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def _commit_account_delete_aws(self, cloud_account_uuid):
    """Commits  Delete AWS Account in Polaris

    Arguments:
        polaris_account_id {str} -- Account ID to commit delete in Polaris
    """
    try:
        query_name = "accounts_aws_delete_commit"
        variables = {
            "cloud_account_uuid": cloud_account_uuid
        }
        return self._query(query_name, variables)
    except Exception:
        raise


def _destroy_aws_stack(self, stack_region, stack_name, profile='', aws_id=None, aws_secret=None):
    """Commits  Destroy cloudformation stack (Rubrik)

    Arguments:
        stack_region {string} -- Single region name from Polaris
        stack_name {string} -- Single stack name from Polaris
    """
    import boto3
    from botocore.exceptions import WaiterError

    if profile:
        boto3.setup_default_session(profile_name=profile)
    elif aws_id and aws_secret:
        boto3.setup_default_session(aws_access_key_id=aws_id, aws_secret_access_key=aws_secret)

    client = boto3.client('cloudformation', region_name=stack_region)
    try:
        self.delete_stack = client.delete_stack(StackName=stack_name)
    except Exception as e:
        print('Stack deletion failed with error:\n  {}'.format(str(e)))

    waiter = client.get_waiter('stack_delete_complete')

    try:
        waiter.wait(StackName=stack_name)
    except WaiterError as e:
        raise Exception('Failed to delete stack: {}\n{}'.format(stack_name, e))
    else:
        return


def delete_account_aws(self, profiles=[], all=False, aws_access_key_id=None, aws_secret_access_key=None):
    """Remove AWS account from Polaris

    Args:
        profiles (list): Optional list of local profile names to remove from Polaris
        all (bool): Optional set true to remove all locally configured profiles from Polaris
        aws_access_key_id (str): AWS Access key to import to Polaris
        aws_secret_access_key (str): AWS secret of key to import to polaris

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.delete_account_aws(profiles = ['milanese_profile'])
        >>> rubrik.delete_account_aws(aws_access_key_id='blah', aws_secret_access_key='blah')
        >>> rubrik.delete_account_aws(all = True )
    """
    if aws_access_key_id and aws_secret_access_key:
        self._delete_account_aws(aws_id=aws_access_key_id, aws_secret=aws_secret_access_key)
    elif all or profiles:
        for profile in self._get_aws_profiles():
            if profile in profiles or (all and profile != 'default'):
                self._delete_account_aws(profile = profile)


def _delete_account_aws(self, profile='', aws_id=None, aws_secret=None):
    import re

    try:
        account_id = None
        if profile:
            account_id = self.get_account_aws_native_id(profile=profile)[0]
        elif aws_id and aws_secret:
            account_id = self.get_account_aws_native_id(aws_id=aws_id, aws_secret=aws_secret)[0]

        polaris_account_info = self.get_accounts_aws_detail(account_id)[0]
        self._pp.pprint(polaris_account_info)
        # TODO: Add exception if account does not exist in polaris
        polaris_account_id = polaris_account_info['awsCloudAccount']['id']
        self._disable_account_aws(polaris_account_id)
        self._invoke_account_delete_aws(polaris_account_id)

        for feature_details in polaris_account_info['featureDetails']:
            if feature_details['feature'] == "CLOUD_NATIVE_PROTECTION":
                stack_name = None
                # Move to := post Py38
                # if match := re.search(r'/(.*)/', feature_details['stackArn']):
                if feature_details['stackArn']:
                    match = re.search(r'/(.*)/', feature_details['stackArn'])
                    stack_name = match.group(1)
                for stack_region in feature_details['awsRegions']:
                    stack_region = (re.sub('_', '-', stack_region)).lower()
                    self._destroy_aws_stack(stack_region, stack_name, profile=profile, aws_id=aws_id, aws_secret=aws_secret)

        self._commit_account_delete_aws(polaris_account_id)
    except Exception as e:
        raise Exception("{}: {}".format("_delete_account_aws", e))


def update_account_aws(self, regions=[], all=False, profiles=[], aws_access_key_id=None, aws_secret_access_key=None):
    """Updates AWS account if configured in Polaris (Under Development)
    """
    if aws_access_key_id and aws_secret_access_key:
        self._update_account_aws(aws_id=aws_access_key_id, aws_secret=aws_secret_access_key)
    elif all or profiles:
        for profile in self._get_aws_profiles():
            if profile in profiles or (all and profile != 'default'):
                self._update_account_aws(profile=profile)


def _update_account_aws_initiate(self, _feature, _polaris_account_id):
    try:
        _query_name = "accounts_aws_update_initiate"
        _variables = {
            "polaris_account_id": _polaris_account_id,
            "aws_native_protection_feature": [_feature]
        }
        self._pp.pprint(_variables)
        return self._query(_query_name, _variables)
    except Exception as e:
        print(e)


def _update_account_aws(self, profile=None, aws_id=None, aws_secret=None,  _aws_account_id = '', _aws_account_name = None):
    if profile:
        _aws_account_id, _aws_account_name = self.get_account_aws_native_id(profile=profile)
    elif aws_id and aws_secret:
        _aws_account_id, _aws_account_name = self.get_account_aws_native_id(aws_id=aws_id, aws_secret=aws_secret)
    if _aws_account_id  == '':
        return
    else:
        _polaris_account_info = self.get_accounts_aws_detail(_aws_account_id)['awsCloudAccounts']
        if not _polaris_account_info:
            return
        for _feature in _polaris_account_info[0]['featureDetails']:
            if _feature['feature'] == "CLOUD_NATIVE_PROTECTION":
                if _feature['status'] == 'MISSING_PERMISSIONS':
                    _update_info = self._update_account_aws_initiate(_feature['feature'], _polaris_account_info[0]['awsCloudAccount']['id'])
                    self._pp.pprint(_update_info)
                if _feature['status'] == 'DISCONNECTED':
                    print("account needs to be recreated")


def _get_account_gcp_project_uuid_by_string(self, search_text):
    try:
        _query_name = "accounts_gcp"
        _variables = {
            "filter": search_text
        }
        return self._query(_query_name, _variables)
    except Exception as e:
        raise PolarisException("Problem getting GCP project uuid from Polaris: {}".format(search_text))


def _get_account_map_aws(self):
    account_detail = self.get_accounts_aws_detail("")['awsCloudAccounts']
    o = {}
    for i in account_detail:
        o[i['awsCloudAccount']['nativeId']] = {}
        o[i['awsCloudAccount']['nativeId']]['id'] = i['awsCloudAccount']['id']
        o[i['awsCloudAccount']['nativeId']]['account_name'] = i['awsCloudAccount']['accountName']
        for f in i['featureDetails']:
            if f['feature'] == 'CLOUD_NATIVE_PROTECTION':
                o[i['awsCloudAccount']['nativeId']]['status'] = f['status']
                o[i['awsCloudAccount']['nativeId']]['regions'] = {}
                for r in f['awsRegions']:
                    o[i['awsCloudAccount']['nativeId']]['regions'][r] = {}
    return o


def add_project_gcp(self, service_account_auth_key_file=None, gcp_native_project_id=None, gcp_native_project_number=None, gcp_native_project_name=None):
    """Add GCP project to Polaris

    Args:
        service_account_auth_key_file (str): Filename of SA .json file
        gcp_native_project_id (str): Project_Id of GCP Project to add

        gcp_native_project_number (str): GCP Project number if ommiting SA
        gcp_native_project_name (str): GCP Project name if omitting SA

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>>  rubrik.add_project_gcp(service_account_auth_key_file="/home/peterm/.google.milanese.json", gcp_native_project_id="home-network-274622")
    """
    if service_account_auth_key_file and not gcp_native_project_name and not gcp_native_project_number:
        project = self._get_gcp_native_project(service_account_auth_key_file=service_account_auth_key_file, project_id=gcp_native_project_id)
        project['service_account_auth_key'] = open(service_account_auth_key_file, 'r').read()
    elif gcp_native_project_name and gcp_native_project_number and gcp_native_project_id and not service_account_auth_key_file:
        project = {
            "gcp_native_project_name": gcp_native_project_name,
            "gcp_native_project_number": int(gcp_native_project_number),
            "gcp_native_project_id": gcp_native_project_id
        }
    else:
        raise PolarisException("Could not add GCP Project, please checkk inputs")
    try:
        _query_name = "accounts_gcp_project_add"
        _variables = project
        _request = self._query(_query_name, _variables)
        if not _request:
            raise PolarisException("Problem adding GCP Project to Polaris: {}".format(gcp_native_project_id))
    except Exception as e:
        raise PolarisException("Problem adding GCP Project to Polaris: {}".format(gcp_native_project_id))


def delete_project_gcp(self, gcp_native_project_id=None, delete_snapshots=False):
    """Remove GCP project from Polaris

    Args:
        gcp_native_project_id (str): Project_Id of GCP Project to remove
        delete_snapshots (bool): Should snapshots be removed from Polaris

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.delete_project_gcp(gcp_native_project_id="home-network-274622")
    """
    try:
        record = self._get_account_gcp_project(search_text=gcp_native_project_id)[0]
    except Exception:
        raise PolarisException("Project does not exist in Polaris : {}".format(gcp_native_project_id))
    if record['featureDetail']['status'] == "CONNECTED":
        disable_id = self._get_account_gcp_project_uuid_by_string(str(record['project']['projectNumber']))[0]['id']
        disable_response = self._disable_account_gcp_project(project_uuid=disable_id)
        if not disable_response:
            raise PolarisException("Problem disabling protection on project: {}".format(gcp_native_project_id))
        task_results = self._monitor_task([disable_response])
        if "SUCC" in task_results['status']:
            self._delete_account_gcp_project(project_uuid=record['project']['id'])
        else:
            raise PolarisException("Failed to disable project {}".format(gcp_native_project_id))
    if "DISABLED" in record['featureDetail']['status']:
        self._delete_account_gcp_project(project_uuid=record['project']['id'])


def _disable_account_gcp_project(self, project_uuid=None, delete_snapshots=False):
    try:
        _query_name = "accounts_gcp_project_disable"
        _variables = {
            "rubrik_project_id": project_uuid,
            "delete_snapshots": delete_snapshots
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem disabling GCP Project in Polaris: {}".format(project_uuid))


def _get_account_gcp_project(self, search_text):
    try:
        _query_name = "accounts_gcp_projects"
        _variables = {
            "status_filters": [],
            "search_text": search_text
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem getting GCP Project from Polaris: {}".format(search_text))


def set_account_gcp_default_sa(self, service_account_auth_key_file=None, service_account_name=None):
    """Set default SA Key for GCP

    Args:
        service_account_auth_key_file (str): Filename of SA key file
        service_account_name (bool): Name to reference SA

    Returns:
        dict: Status if unsuccessful

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.set_account_gcp_default_sa(service_account_auth_key_file = "file.json", service_account_name = "sa-2021-03")
    """
    try:
        _query_name = "accounts_gcp_default_sa_set"
        _variables = {
            "name": service_account_name,
            "jwt_config": open(service_account_auth_key_file, 'r').read()
        }
        _request = self._query(_query_name, _variables)
        return _request
    except Exception as e:
        raise PolarisException("Problem setting GCP Project default SA: {}".format(e))


def get_account_gcp_default_sa(self):
    """Get default SA Key for GCP

    Returns:
        dict: Status of query results

    Raises:
        RequestException: If the query to Polaris returned an error

    Examples:
        >>> rubrik.get_account_gcp_default_sa()
    """
    try:
        _query_name = "accounts_gcp_default_sa_get"
        _request = self._query(_query_name, None)
        return _request
    except Exception as e:
        raise PolarisException("Problem getting GCP Project default SA: {}".format(e))


def _delete_account_gcp_project(self, project_uuid=None):
    try:
        _query_name = "accounts_gcp_project_delete"
        _variables = {
            "native_protection_ids": [project_uuid],
            "shared_vpc_host_project_ids": [],
            "cloud_account_project_ids": []
        }
        _request = self._query(_query_name, _variables)
    except Exception as e:
        raise PolarisException("Problem deleting GCP Project from Polaris: {}".format(project_uuid))


def _get_account_gcp_permissions_cnp(self):
    try:
        _query_name = "accounts_gcp_permissions"
        _request = self._query(_query_name, None)
        o = []
        for p in _request:
            o.append(p['permission'])
        return o
    except Exception as e:
        raise PolarisException("Problem getting GCP permission requirements from Polaris {}".format(e))


def _get_gcp_native_project(self, service_account_auth_key_file, project_id=None):
    from googleapiclient import discovery
    from googleapiclient.errors import HttpError
    from oauth2client.service_account import ServiceAccountCredentials
    credentials = ServiceAccountCredentials.from_json_keyfile_name(service_account_auth_key_file)
    service = discovery.build('cloudresourcemanager', 'v1', credentials=credentials)

    # Check permissions requirement from Polaris against GCP using SA
    permission_required = self._get_account_gcp_permissions_cnp()
    permissions = {"permissions": permission_required}
    self._pp.pprint(permissions)
    try:
        request = service.projects().testIamPermissions(resource=project_id, body=permissions)
        permissions_set = request.execute()
        self._pp.pprint(permissions_set)
        permission_delta = list(set(permission_required) - set(permissions_set['permissions']))
    except HttpError as e:
        raise PolarisException("Failed to lookup SA permissions from GCP: {}".format(e))
    if len(permission_delta) > 0:
        raise PolarisException("Permissions are incorrect for Service Account. Requires additional: {}".format(permission_delta))

    # Get project details from GCP
    request = service.projects().get(projectId=project_id)
    response = request.execute()
    project = {'gcp_native_project_name': response['name'], 'gcp_native_project_id': response['projectId'], 'gcp_native_project_number': int(response['projectNumber'])}
    try:
        if response['parent']['type'] == 'organization':
            name = 'organizations/{}'.format(response['parent']['id'])
            request = service.organizations().get(name=name)
            response = request.execute()
            if 'displayName' in response:
                project['organization_name'] = response['displayName']
    except HttpError as e:
        if 'permission' in str(e):
            project['organization_name'] = response['parent']['id']
        else:
            raise PolarisException("Problem getting GCP organization: {}".format(e))
    except Exception as e:
        raise PolarisException("Problem getting GCP project details: {}".format(e))
    return project

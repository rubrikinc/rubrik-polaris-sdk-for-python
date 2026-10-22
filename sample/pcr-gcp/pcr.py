#! /usr/bin/env python3
import argparse
import docker
import json
import logging
import sys
from google.oauth2 import service_account
from google.auth.transport.requests import Request
from rubrik_polaris.rubrik_polaris import PolarisClient

_PCR_OIDC_AUDIENCE = 'https://rubrik.com/exocompute/pcr/gcp'


def parse_arguments():
    parser = argparse.ArgumentParser(
        description='Configure GCP Private Container Registry (PCR) for Rubrik Exocompute'
    )
    parser.add_argument(
        '--gcpProjectNativeId',
        dest='gcp_project_native_id',
        help='GCP Project Native ID for which you want to configure PCR',
        required=True,
    )
    parser.add_argument(
        '--gcpServiceAccountEmail',
        dest='gcp_sa_email',
        help='GCP Service Account email used to pull images from Rubrik GAR '
             'and push to the customer private container registry',
        required=True,
    )
    parser.add_argument(
        '--gcpSAKeyFile',
        dest='gcp_sa_key_file',
        help='Path to the GCP Service Account JSON key file used for '
             'Docker authentication to both Rubrik GAR and the customer registry',
        required=True,
    )
    parser.add_argument(
        '--customerGarUrl',
        dest='customer_gar_url',
        help='Customer private Google Artifact Registry repository URL '
             '(e.g. us-docker.pkg.dev/<project>/<repository>)',
        required=True,
    )
    parser.add_argument('-d', '--domain', dest='domain', help='Polaris Domain')
    parser.add_argument('-k', '--keyfile', dest='json_keyfile', help='JSON Keyfile')
    parser.add_argument('-p', '--password', dest='password', help='Polaris Password')
    parser.add_argument('-r', '--root', dest='root_domain', help='Polaris Root Domain')
    parser.add_argument('-u', '--username', dest='username', help='Polaris UserName')
    parser.add_argument(
        '-v', '--verbose',
        help='Be verbose',
        action='store_const',
        dest='loglevel',
        const=logging.INFO,
    )
    parser.add_argument(
        '--debug',
        help='Print lots of debugging statements',
        action='store_const',
        dest='loglevel',
        const=logging.DEBUG,
        default=logging.WARNING,
    )
    parser.add_argument('--insecure', help='Deactivate SSL Verification', action='store_true')
    return parser.parse_args()


def setup_logging(args):
    logging.basicConfig(stream=sys.stderr, level=args.loglevel)


def check_arguments(args):
    if not (args.json_keyfile or (args.username and args.password and args.domain)):
        sys.exit(
            'Error: Login credentials not specified. You must specify either '
            'a JSON keyfile or a username, password, and domain.'
        )


def setup_polaris_client(args):
    try:
        if args.json_keyfile:
            rubrik = PolarisClient(json_keyfile=args.json_keyfile, insecure=args.insecure)
        else:
            rubrik = PolarisClient(
                domain=args.domain,
                username=args.username,
                password=args.password,
                root_domain=args.root_domain,
                insecure=args.insecure,
            )
        return rubrik
    except Exception as err:
        print(f'Error initializing PolarisClient: {err}')
        sys.exit(1)


def get_gcp_account_details(rubrik):
    variables = {
        'feature': 'EXOCOMPUTE',
        'projectStatusFilters': [],
        'projectSearchText': '',
    }
    try:
        query = '''
        query ($feature: CloudAccountFeature!, $projectStatusFilters: [CloudAccountStatus!]!, $projectSearchText: String!) {
            allGcpCloudAccountProjectsByFeature(
                feature: $feature,
                projectStatusFilters: $projectStatusFilters,
                projectSearchText: $projectSearchText
            ) {
                project {
                    id
                    projectId
                    name
                }
            }
        }
        '''
        response = rubrik._query_raw(raw_query=query, operation_name=None, variables=variables, timeout=60)
        logging.debug(json.dumps(response, indent=2))
        return response
    except Exception as err:
        print(f'Error: Unable to retrieve GCP account details: {err}')
        sys.exit(1)


def set_private_container_registry(rubrik, cloud_account_id, gcp_sa_email, ownership_token, customer_gar_url):
    print(f'Setting private container registry for GCP project account {cloud_account_id}')
    variables = {
        'input': {
            'exocomputeAccountId': cloud_account_id,
            'registryUrl': customer_gar_url,
            'cloudType': 'GCP',
            'pcrGcpImagePullDetails': {
                'serviceAccountEmail': gcp_sa_email,
                'serviceAccountOwnershipToken': ownership_token,
            },
        }
    }
    try:
        mutation = '''
        mutation SetPrivateContainerRegistry($input: SetPrivateContainerRegistryInput!) {
            setPrivateContainerRegistry(input: $input)
        }
        '''
        rubrik._query_raw(raw_query=mutation, operation_name=None, variables=variables, timeout=60)
    except Exception as err:
        print(f'Error: Unable to set the private container registry: {err}')
        sys.exit(1)


def get_private_container_registry(rubrik, cloud_account_id, account_name):
    print('Getting currently approved PCR bundle version numbers')
    variables = {'input': {'exocomputeAccountId': cloud_account_id}}
    try:
        query = '''
        query PrivateContainerRegistry($input: PrivateContainerRegistryInput!) {
            privateContainerRegistry(input: $input) {
                pcrDetails {
                    registryUrl
                    imagePullDetails {
                        ... on PcrGcpImagePullDetails {
                            serviceAccountEmail
                        }
                    }
                }
                pcrLatestApprovedBundleVersion
            }
        }
        '''
        response = rubrik._query_raw(raw_query=query, operation_name=None, variables=variables, timeout=60)
        version = response['data']['privateContainerRegistry']['pcrLatestApprovedBundleVersion']
        print(f'Current approved bundle version is: {version}')
        return response
    except Exception as err:
        print(
            f'Error: Unable to get the private container registry information '
            f'for exocompute account {account_name}: {err}'
        )
        sys.exit(1)


def get_exotask_image_bundle(rubrik):
    try:
        query = '''
        query ExotaskImageBundle {
            exotaskImageBundle {
                gcpImages {
                    bundleVersion
                    repoUrl
                    bundleImages {
                        name
                        tag
                        sha
                    }
                }
            }
        }
        '''
        response = rubrik._query_raw(raw_query=query, operation_name=None, variables=None, timeout=60)
        logging.debug(json.dumps(response, indent=2))
        bundle_version = response['data']['exotaskImageBundle']['gcpImages']['bundleVersion']
        print(f'New bundle version is: {bundle_version}')
        return response
    except Exception as err:
        print(f'Error: Unable to retrieve exotaskImageBundle: {err}')
        sys.exit(1)


def get_bundle_version(image_bundle):
    return image_bundle['data']['exotaskImageBundle']['gcpImages']['bundleVersion']


def compare_bundle_versions(current_version, new_version):
    # No bundle has been approved yet on the first run.
    if current_version and current_version >= new_version:
        print(
            'New bundle version is the same or lower than the current approved '
            'bundle version. Exiting.'
        )
        sys.exit(0)


def check_gcp_sa_key_file(gcp_sa_key_file, gcp_sa_email):
    try:
        credentials = service_account.Credentials.from_service_account_file(gcp_sa_key_file)
    except Exception as err:
        print(f'Error: Unable to load GCP SA key file {gcp_sa_key_file}: {err}')
        sys.exit(1)
    if credentials.service_account_email != gcp_sa_email:
        print(
            f'Error: GCP SA key file belongs to {credentials.service_account_email}, '
            f'not {gcp_sa_email}.'
        )
        sys.exit(1)


def get_gcp_access_token(gcp_sa_key_file):
    """Return an OAuth2 access token used for Docker authentication to GAR."""
    try:
        credentials = service_account.Credentials.from_service_account_file(
            gcp_sa_key_file,
            scopes=['https://www.googleapis.com/auth/cloud-platform'],
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as err:
        print(f'Error: Unable to obtain GCP access token from SA key file: {err}')
        sys.exit(1)


def get_gcp_ownership_token(gcp_sa_key_file):
    """Return an OIDC identity token used by RSC to verify SA ownership."""
    try:
        credentials = service_account.IDTokenCredentials.from_service_account_file(
            gcp_sa_key_file,
            target_audience=_PCR_OIDC_AUDIENCE,
        )
        credentials.refresh(Request())
        return credentials.token
    except Exception as err:
        print(f'Error: Unable to obtain GCP ownership token from SA key file: {err}')
        sys.exit(1)


def login_to_gar(registry_host, access_token, docker_client):
    try:
        docker_client.login(
            username='oauth2accesstoken',
            password=access_token,
            registry=registry_host,
            reauth=True,
        )
        return {'username': 'oauth2accesstoken', 'password': access_token}
    except Exception as err:
        print(f'Error: Unable to login to GAR registry {registry_host}: {err}')
        sys.exit(1)


def consume_docker_stream(stream):
    # The Docker API reports pull/push failures as stream entries rather than
    # raising, so surface them as exceptions.
    for line in stream:
        logging.debug(json.dumps(line, indent=2))
        if 'error' in line:
            raise RuntimeError(line['error'])


def pull_images(image_bundle, rsc_repo_fqdn, auth_config, docker_api_client):
    for image in image_bundle['data']['exotaskImageBundle']['gcpImages']['bundleImages']:
        image_name = f'{rsc_repo_fqdn}/{image["name"]}'
        if image['tag']:
            print(f'Pulling {image["name"]} with tag {image["tag"]}')
            try:
                consume_docker_stream(docker_api_client.pull(
                    image_name,
                    tag=image['tag'],
                    stream=True,
                    auth_config=auth_config,
                    decode=True,
                ))
            except Exception as err:
                print(f'Error: Image pull failed for {image["name"]} with tag {image["tag"]}: {err}')
                sys.exit(1)
        elif image['sha']:
            print(f'Pulling {image["name"]} with sha {image["sha"]}')
            try:
                consume_docker_stream(docker_api_client.pull(
                    image_name,
                    tag=f'sha256:{image["sha"]}',
                    stream=True,
                    auth_config=auth_config,
                    decode=True,
                ))
            except Exception as err:
                print(f'Error: Image pull failed for {image["name"]} with sha {image["sha"]}: {err}')
                sys.exit(1)
        else:
            print(f'Error: No tag or sha found for {image["name"]} in {rsc_repo_fqdn} bundle.')
            sys.exit(1)


def scan_images(image_bundle):
    print('\nScanning images for vulnerabilities')
    for image in image_bundle['data']['exotaskImageBundle']['gcpImages']['bundleImages']:
        if image['tag']:
            print(f'Scanning {image["name"]} with tag {image["tag"]}')
            # <Insert Image Scanning Tool Here>
        elif image['sha']:
            print(f'Scanning {image["name"]} with sha {image["sha"]}')
            # <Insert Image Scanning Tool Here>
        else:
            print(f'Error: No tag or sha found for {image["name"]} in bundle.')
            sys.exit(1)
    print('')


def tag_and_push_images(image_bundle, rsc_repo_fqdn, customer_gar_url, auth_config, docker_api_client):
    bundle_version = get_bundle_version(image_bundle)
    for image in image_bundle['data']['exotaskImageBundle']['gcpImages']['bundleImages']:
        print('')
        source_image = f'{rsc_repo_fqdn}/{image["name"]}'
        target_image = f'{customer_gar_url}/{image["name"]}'

        if image['tag']:
            print(
                f'Tagging and pushing {image["name"]} with tag {image["tag"]} '
                f'to {target_image}:{bundle_version}'
            )
            try:
                docker_api_client.tag(f'{source_image}:{image["tag"]}', f'{target_image}:{bundle_version}')
            except Exception as err:
                print(f'Error: Image tag failed for {image["name"]} with tag {image["tag"]}: {err}')
                sys.exit(1)
        elif image['sha']:
            print(
                f'Tagging and pushing {image["name"]} with sha {image["sha"]} '
                f'to {target_image}:{bundle_version}'
            )
            try:
                docker_api_client.tag(
                    f'{source_image}@sha256:{image["sha"]}', f'{target_image}:{bundle_version}'
                )
            except Exception as err:
                print(f'Error: Image tag failed for {image["name"]} with sha {image["sha"]}: {err}')
                sys.exit(1)
        else:
            print(f'Error: No tag or sha found for {image["name"]} in bundle.')
            sys.exit(1)

        print(f'Pushing {target_image}:{bundle_version}')
        try:
            consume_docker_stream(docker_api_client.push(
                target_image,
                tag=bundle_version,
                stream=True,
                auth_config=auth_config,
                decode=True,
            ))
        except Exception as err:
            print(f'Error: Image push failed for {image["name"]} with tag {bundle_version}: {err}')
            sys.exit(1)


def accept_container_bundle(rubrik, bundle_version):
    variables = {
        'input': {
            'approvalStatus': 'ACCEPTED',
            'bundleVersion': bundle_version,
        }
    }
    try:
        mutation = '''
        mutation SetBundleApprovalStatus($input: SetBundleApprovalStatusInput!) {
            setBundleApprovalStatus(input: $input)
        }
        '''
        rubrik._query_raw(raw_query=mutation, operation_name=None, variables=variables, timeout=60)
        print(f'\n\nBundle {bundle_version} has been accepted.')
    except Exception as err:
        print(f'Error: Unable to accept container bundle: {err}')
        sys.exit(1)


def main():
    args = parse_arguments()
    setup_logging(args)
    check_arguments(args)
    rubrik = setup_polaris_client(args)

    print(
        f'Configuring PCR for GCP project {args.gcp_project_native_id} '
        f'with customer GAR URL {args.customer_gar_url} '
        f'and GCP service account {args.gcp_sa_email}'
    )

    cloud_account_id = None
    cloud_account_name = None

    gcp_projects = get_gcp_account_details(rubrik)
    for entry in gcp_projects['data']['allGcpCloudAccountProjectsByFeature']:
        project = entry['project']
        if project['projectId'] == args.gcp_project_native_id:
            cloud_account_id = project['id']
            cloud_account_name = project['name']
            break

    if not cloud_account_id:
        print(
            f'Error: GCP project {args.gcp_project_native_id} not found or '
            f'not configured for Exocompute in RSC.'
        )
        sys.exit(1)

    check_gcp_sa_key_file(args.gcp_sa_key_file, args.gcp_sa_email)
    ownership_token = get_gcp_ownership_token(args.gcp_sa_key_file)

    set_private_container_registry(
        rubrik,
        cloud_account_id,
        args.gcp_sa_email,
        ownership_token,
        args.customer_gar_url,
    )

    private_registry = get_private_container_registry(rubrik, cloud_account_id, cloud_account_name)
    new_bundle = get_exotask_image_bundle(rubrik)

    current_version = private_registry['data']['privateContainerRegistry']['pcrLatestApprovedBundleVersion']
    new_version = get_bundle_version(new_bundle)
    compare_bundle_versions(current_version, new_version)

    rsc_repo_fqdn = new_bundle['data']['exotaskImageBundle']['gcpImages']['repoUrl']
    registry_host = rsc_repo_fqdn.split('/')[0]

    docker_client = docker.from_env()
    docker_api_client = docker_client.api
    access_token = get_gcp_access_token(args.gcp_sa_key_file)
    rsc_auth_config = login_to_gar(registry_host, access_token, docker_client)

    pull_images(new_bundle, rsc_repo_fqdn, rsc_auth_config, docker_api_client)
    scan_images(new_bundle)

    # Refresh the access token since pulling the bundle can outlast its lifetime.
    access_token = get_gcp_access_token(args.gcp_sa_key_file)
    customer_registry_host = args.customer_gar_url.split('/')[0]
    customer_auth_config = login_to_gar(customer_registry_host, access_token, docker_client)

    tag_and_push_images(new_bundle, rsc_repo_fqdn, args.customer_gar_url, customer_auth_config, docker_api_client)
    accept_container_bundle(rubrik, new_version)


if __name__ == '__main__':
    main()

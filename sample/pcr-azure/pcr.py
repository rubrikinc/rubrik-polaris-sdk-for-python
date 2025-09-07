#! /usr/bin/env python3
import argparse
import base64
import docker
import json
import logging
import os
import pprint
import subprocess
import sys
from rubrik_polaris.rubrik_polaris import PolarisClient
from azure.cli.core import get_default_cli

pp = pprint.PrettyPrinter(indent=2)

# RUBRIK_ACR_NAME is the default ACR name for dev. This can be
# different for production environment.
RUBRIK_ACR_NAME = "centralacrdev"
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def parse_arguments():
    parser = argparse.ArgumentParser()
    parser.add_argument('--azureCustomerAppId', dest='azureCustomerAppId', help='Azure Customer App ID used to download image from Rubrik ACR', default=None, required=False)
    parser.add_argument('--azureCustomerAppSecret', dest='azureCustomerAppSecret', help='Azure Customer App secret used to download image from Rubrik ACR', default=None, required=False)
    parser.add_argument('--azureCustomerAppTenantId', dest='azureCustomerAppTenantId', help='Azure Customer App Tenant ID used to download image from Rubrik ACR', default=None, required=False)
    parser.add_argument('--azureSubscriptionNativeId', dest='azureSubscriptionNativeId', help='Azure Subscription native ID for which you want to configure PCR', default=None, required=False)
    parser.add_argument('--rubrikAcrName', dest='rubrikAcrName', help='Rubrik ACR name from where we want to pull images', default=None, required=True)
    parser.add_argument('-d', '--domain', dest='domain', help="Polaris Domain", default=None)
    parser.add_argument('-k', '--keyfile', dest='json_keyfile', help="JSON Keyfile", default=None)
    parser.add_argument('-p', '--password', dest='password', help="Polaris Password", default=None)
    parser.add_argument('-r', '--root', dest='root_domain', help="Polaris Root Domain", default=None)
    parser.add_argument('-u', '--username', dest='username', help="Polaris UserName", default=None)
    parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO)
    parser.add_argument('--debug', help="Print lots of debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
    parser.add_argument('--insecure', help='Deactivate SSL Verification', action="store_true")
    parser.add_argument('--pcrAuth', dest='pcrAuth', help='Set to "PWD" to use username/password based private container registry', default="PWD", required=False, choices=['PWD'])
    parser.add_argument('--pcrFqdn', dest='pcrFqdn', help='Private Container Registry URL', default=None, required=True)
    parser.add_argument('--pcrPassword', dest='pcrPassword', help='Password for the private container registry.', default=None, required=False)
    parser.add_argument('--pcrUsername', dest='pcrUsername', help='Username for the private container registry.', default=None, required=False)
    args = parser.parse_args()
    return args

def setup_logging(args):
    # logging.basicConfig(level=args.loglevel)
    logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

def check_arguments(args):
    if args.pcrAuth == "PWD" and not (args.pcrPassword and args.pcrUsername):
        sys.exit('Error: Username/Password authentication to private container registry specified (--pcrAuth PWD), however, --pcrPassword or --pcrUsername not specified.')
    if not (args.json_keyfile or (args.username and args.password and args.domain)):
        sys.exit('Error: Login credentials not specified. You must specify either a JSON keyfile or a username, password, and domain.')
    # Verify that app ID, secret, tenant ID, azureSubscriptionNativeId are provided
    if not (args.azureCustomerAppId and args.azureCustomerAppSecret and args.azureCustomerAppTenantId and args.azureSubscriptionNativeId):
        sys.exit('Error: Azure Customer App ID, secret, tenant ID and azure subscription native Id must be provided for Azure cloud type.')

def setup_polaris_client(args):
    try:
        if args.json_keyfile:
            rubrik = PolarisClient(json_keyfile=args.json_keyfile, insecure=args.insecure)
        else:
            rubrik = PolarisClient(domain=args.domain, username=args.username, password=args.password, root_domain=args.root_domain, insecure=args.insecure)
        return rubrik
    except Exception as err:
        print(f"Error initializing PolarisClient: {err}")
        sys.exit(1)

def get_azure_account_details(rubrik):
    variables = {"azureExocomputeSearchQuery": ""}
    try:
        query = '''
        query ($azureExocomputeSearchQuery: String!) {
            allAzureExocomputeConfigsInAccount(azureExocomputeSearchQuery: $azureExocomputeSearchQuery) {
                azureCloudAccount {
                    id
                    nativeId
                    name
                }
            }
        }
        '''
        allAzureExocomputeConfigs = rubrik._query_raw(raw_query=query, operation_name=None, variables=variables, timeout=60)
        logging.debug(json.dumps(allAzureExocomputeConfigs, indent=2))
        return allAzureExocomputeConfigs
    except Exception as err:
        print(f"Error: Unable to retrieve the Azure account details: {err}")
        sys.exit(1)

def set_private_container_registry(rubrik, cloudAccountId, azureCustomerAppId, pcrFqdn):
    input_details = {
        "exocomputeAccountId": cloudAccountId,
        "registryUrl": pcrFqdn,
        "cloudType": "AZURE",
    }
    print(f"Setting private container registry for Azure customer app ID {azureCustomerAppId}")
    input_details["pcrAzureImagePullDetails"] = {"customerAppId": azureCustomerAppId}

    variables = {"input": input_details}
    try:
        mutation = '''
        mutation SetPrivateContainerRegistry($input: SetPrivateContainerRegistryInput!) {
            setPrivateContainerRegistry(input: $input)
        }
        '''
        rubrik._query_raw(raw_query=mutation, operation_name=None, variables=variables, timeout=60)
    except Exception as err:
        print(f"Error: Unable to set the private container registry: {err}")
        sys.exit(1)

def get_private_container_registry(rubrik, cloudAccountId, accountName):
    print("Getting currently approved PCR bundle version numbers")
    variables = {"input": {"exocomputeAccountId": cloudAccountId}}
    try:
        query = '''
        query PrivateContainerRegistry($input: PrivateContainerRegistryInput!) {
            privateContainerRegistry(input: $input) {
                pcrDetails {
                    registryUrl
                    imagePullDetails {
                        ... on PcrAzureImagePullDetails {
                            customerAppId
                        }
                    }
                }
                pcrLatestApprovedBundleVersion
            }
        }
        '''
        privateContainerRegistry = rubrik._query_raw(raw_query=query, operation_name=None, variables=variables, timeout=60)
        version = privateContainerRegistry['data']['privateContainerRegistry']['pcrLatestApprovedBundleVersion']
        print(f"Current approved bundle version is: {version}")
        return privateContainerRegistry
    except Exception as err:
        print(f"Error: Unable to get the private container registry information for exocompute account {accountName}: {err}")
        sys.exit(1)

def get_exotask_image_bundle(rubrik):
    variables = {"input": {}}
    try:
        query = '''
        query ExotaskImageBundle {
            exotaskImageBundle {
                azureImages{
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
        exoTaskImageBundle = rubrik._query_raw(raw_query=query, operation_name=None, variables=variables, timeout=60)
        logging.debug(json.dumps(exoTaskImageBundle, indent=2))
        print(f"New bundle version is: {exoTaskImageBundle['data']['exotaskImageBundle']['azureImages']['bundleVersion']}")
        return exoTaskImageBundle
    except Exception as err:
        print(f"Error: Unable to retrieve exotaskImageBundle: {err}")
        sys.exit(1)

def get_bundle_version_from_image_bundle(exoTaskImageBundle):
    return exoTaskImageBundle['data']['exotaskImageBundle']['azureImages']['bundleVersion']

def compare_bundle_versions(current_version, new_version):
    if current_version >= new_version:
        print("New bundle version is the same or lower than the current approved bundle version. Exiting.")
        sys.exit(0)

def pull_images(exoTaskImageBundle, rscRepoFqdn, auth_config_payload, docker_api_client):
    for image in exoTaskImageBundle['data']['exotaskImageBundle']['azureImages']['bundleImages']:
        image_name = f"{rscRepoFqdn}/{image['name']}"
        if image['tag']:
            print(f"Pulling {image['name']} with tag {image['tag']}")
            try:
                for line in docker_api_client.pull(image_name, tag=image['tag'], stream=True, auth_config=auth_config_payload, decode=True):
                    logging.debug(json.dumps(line, indent=2))
            except Exception as err:
                print(f"Error: Image pull failed for {image['name']} with tag {image['tag']}: {err}")
                sys.exit(1)
        elif image['sha']:
            print(f"Pulling {image['name']} with sha {image['sha']}")
            try:
                for line in docker_api_client.pull(image_name, tag=f"sha256:{image['sha']}", stream=True, auth_config=auth_config_payload, decode=True):
                    logging.debug(json.dumps(line, indent=2))
            except Exception as err:
                print(f"Error: Image pull failed for {image['name']} with sha {image['sha']}: {err}")
                sys.exit(1)
        else:
            print(f"Error: No tag or sha found for {image['name']} in {rscRepoFqdn} bundle.")
            sys.exit(1)

def scan_images(exoTaskImageBundle):
    print("\nScanning images for vulnerabilities")
    for image in exoTaskImageBundle['data']['exotaskImageBundle']['azureImages']['bundleImages']:
        if image['tag']:
            print(f"Scanning {image['name']} with tag {image['tag']}")
            # Implement scanning logic here
        elif image['sha']:
            print(f"Scanning {image['name']} with sha {image['sha']}")
            # Implement scanning logic here
        else:
            print(f"Error: No tag or sha found for {image['name']} in bundle.")
            sys.exit(1)
    print("")

def login_to_customer_pcr(args, pcrFqdn, pcrRegion):
    dockerClient = docker.from_env()
    if args.pcrAuth == "PWD":
        try:
            auth_config_payload = {'username': args.pcrUsername, 'password': args.pcrPassword}
            dockerClient.login(username=args.pcrUsername, password=args.pcrPassword, registry=pcrFqdn, reauth=True)
            return auth_config_payload, docker.APIClient(base_url='unix://var/run/docker.sock')
        except Exception as err:
            print(f"Error: Unable to login to customer PCR: {err}")
            sys.exit(1)

def tag_and_push_images(args, exoTaskImageBundle, rscRepoFqdn, pcrFqdn, auth_config_payload, docker_api_client, pcrRegion):
    for image in exoTaskImageBundle['data']['exotaskImageBundle']['azureImages']['bundleImages']:
        print("")
        repositoryName = image['name']
        source_image = f"{rscRepoFqdn}/{image['name']}"
        target_image = f"{pcrFqdn}/{image['name']}"
        tag = exoTaskImageBundle['data']['exotaskImageBundle']['azureImages']['bundleVersion']
        if image['tag']:
            print(f"Tagging and pushing {image['name']} with tag {image['tag']} to {target_image}:{tag}")
            docker_api_client.tag(f"{source_image}:{image['tag']}", f"{target_image}:{tag}")
        elif image['sha']:
            print(f"Tagging and pushing {image['name']} with sha {image['sha']} to {target_image}:{tag}")
            docker_api_client.tag(f"{source_image}@sha256:{image['sha']}", f"{target_image}:{tag}")
        else:
            print(f"Error: No tag or sha found for {image['name']} in bundle.")
            sys.exit(1)
        print(f"Pushing {target_image}:{tag}")
        try:
            for line in docker_api_client.push(target_image, tag=tag, stream=True, auth_config=auth_config_payload, decode=True):
                logging.debug(json.dumps(line, indent=2))
        except Exception as err:
            print(f"Error: Image push failed for {image['name']} with tag {tag}: {err}")
            sys.exit(1)

def accept_container_bundle(rubrik, bundleVersion):
    variables = {"input": {"approvalStatus": "ACCEPTED", "bundleVersion": bundleVersion}}
    try:
        mutation = '''
        mutation SetBundleApprovalStatus($input: SetBundleApprovalStatusInput!) {
            setBundleApprovalStatus(input: $input)
        }
        '''
        rubrik._query_raw(raw_query=mutation, operation_name=None, variables=variables, timeout=60)
        print(f"\n\nBundle {bundleVersion} has been accepted.")
    except Exception as err:
        print(f"Error: Unable to accept container bundle: {err}")
        sys.exit(1)

def main():
    args = parse_arguments()
    setup_logging(args)
    check_arguments(args)
    rubrik = setup_polaris_client(args)

    cloudAccountId = None
    cloudAccountName = None

    # Get cloud account ID using Native ID
    azureConfigs = get_azure_account_details(rubrik)
    for config in azureConfigs['data']['allAzureExocomputeConfigsInAccount']:
        if config['azureCloudAccount']['nativeId'] == args.azureSubscriptionNativeId:
            cloudAccountId = config['azureCloudAccount']['id']
            cloudAccountName = config['azureCloudAccount']['name']
            break
    if not cloudAccountId:
        print(f"Error: Azure customer app ID {args.azureCustomerAppId} not found.")
        sys.exit(1)



    set_private_container_registry(rubrik, cloudAccountId, args.azureCustomerAppId, args.pcrFqdn)
    privateRegistry = get_private_container_registry(rubrik, cloudAccountId, cloudAccountName)
    newBundle = get_exotask_image_bundle(rubrik)
    current_version = privateRegistry['data']['privateContainerRegistry']['pcrLatestApprovedBundleVersion']
    new_version = get_bundle_version_from_image_bundle(newBundle)
    compare_bundle_versions(current_version, new_version)


    pcrRegion = None

    # Login to ACR and pull images

    # az login --service-principal -u azureCustomerAppId -p azureCustomerAppSecret --tenant azureCustomerAppTenantId
    print(get_default_cli().invoke(['login', '--service-principal', '-u', args.azureCustomerAppId, '-p', args.azureCustomerAppSecret, '--tenant', args.azureCustomerAppTenantId]))

    # az acr login --name RUBRIK_ACR_NAME -u azureCustomerAppId -p azureCustomerAppSecret
    print(get_default_cli().invoke(['acr', 'login', '--name', args.rubrikAcrName , '-u', args.azureCustomerAppId, '-p', args.azureCustomerAppSecret]))

    rscRepoFqdn = newBundle['data']['exotaskImageBundle']['azureImages']['repoUrl']
    dockerClient = docker.from_env()
    docker_api_client = docker.APIClient(base_url='unix://var/run/docker.sock')
    pull_images(newBundle, rscRepoFqdn, None, docker_api_client)

    # Scan images
    scan_images(newBundle)

    # Login to customer PCR and push images
    customer_auth_config, _ = login_to_customer_pcr(args, args.pcrFqdn, pcrRegion)
    tag_and_push_images(args, newBundle, rscRepoFqdn, args.pcrFqdn, customer_auth_config, docker_api_client, pcrRegion)

    # Accept Container Bundle
    accept_container_bundle(rubrik, new_version)

if __name__ == '__main__':
    main()
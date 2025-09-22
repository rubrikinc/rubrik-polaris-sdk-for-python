#! /usr/bin/env python3
import argparse
import base64
import boto3
import docker
import json
import logging
import os
import pprint
import subprocess
import sys
from rubrik_polaris.rubrik_polaris import PolarisClient

pp = pprint.PrettyPrinter(indent=2)
#logging.basicConfig(stream=sys.stderr, level=logging.DEBUG)

parser = argparse.ArgumentParser()
parser.add_argument('-a', '--awsAccountid', dest='awsAccountId', help="AWS Account ID used to download images from Rubrik ECR", default=None,required=True)
parser.add_argument('-d', '--domain', dest='domain', help="Polaris Domain", default=None)
parser.add_argument('-k', '--keyfile', dest='json_keyfile', help="JSON Keyfile", default=None)
parser.add_argument('-p', '--password', dest='password', help="Polaris Password", default=None)
parser.add_argument('-r', '--root', dest='root_domain', help="Polaris Root Domain", default=None)
parser.add_argument('-u', '--username', dest='username', help="Polaris UserName", default=None)
parser.add_argument('-v', '--verbose', help="Be verbose", action="store_const", dest="loglevel", const=logging.INFO)
parser.add_argument('--debug', help="Print lots of debugging statements", action="store_const", dest="loglevel", const=logging.DEBUG, default=logging.WARNING)
parser.add_argument('--eksVersion', dest='eksVersion', help='Version of EKS cluster being used for Exocompute', default='1.27', required=True)
parser.add_argument('--insecure', help='Deactivate SSL Verification', action="store_true")
parser.add_argument('--pcrAuth', dest='pcrAuth', help='Set to "ECR" to use ECR based private container registry. Set to "PWD" to use username/password based private container registry', default="ECR", required=False, choices=['ECR', 'PWD'])
parser.add_argument('--pcrFqdn', dest='pcrFqdn', help='Private Container Registry URL', default=None, required=True)
parser.add_argument('--pcrPassword', dest='pcrPassword', help='Password for the private container registry.', default=None, required=False)
parser.add_argument('--pcrUsername', dest='pcrUsername', help='Username for the private container registry.', default=None, required=False)

args = parser.parse_args()
pcrFqdn = args.pcrFqdn

logging.basicConfig(level=args.loglevel)

if args.pcrAuth == "PWD" and not (args.pcrPassword and args.pcrUsername):
    parser.error('Username/Password authentication to private container registry specified (--pcrAuth PWD), however, --pcrPassword or --pcrUsername not specified.')
    
if not (args.json_keyfile or (args.username and args.password and args.domain)):
    parser.error('Login credentials not specified. You must specify either a JSON keyfile or a username, password, and domain.')

try:

### Instantiate with json keyfile
    if args.json_keyfile:
        rubrik = PolarisClient(json_keyfile=args.json_keyfile, insecure=args.insecure)
    else:
### Instantiate with username/password
        rubrik = PolarisClient(domain=args.domain, username=args.username, password=args.password, root_domain=args.root_domain,
                                      insecure=args.insecure)

except Exception as err:
    print(err)
    sys.exit(1)

# Set Private Container Registry (white list AWS account to download images)

variables = {
"awsNativeAccountIdOrNamePrefix": ""
}

try:
    allAwsExocomputeConfigs = rubrik._query_raw(raw_query='query ($awsNativeAccountIdOrNamePrefix: String!) {allAwsExocomputeConfigs(awsNativeAccountIdOrNamePrefix: $awsNativeAccountIdOrNamePrefix) {awsCloudAccount {id nativeId accountName message seamlessFlowEnabled cloudType}}}',
                                      operation_name=None,
                                      variables=variables,
                                      timeout=60)
except Exception as err:
    print("Error: Unable to retrieve the AWS account details.")
    print(err)
    sys.exit(1)

logging.debug(json.dumps(allAwsExocomputeConfigs, indent=2))

# Make sure that all repos are authorized to pull images from Rubrik ECR.
for awsCloudAccount in allAwsExocomputeConfigs['data']['allAwsExocomputeConfigs']:
  if awsCloudAccount['awsCloudAccount']['nativeId'] == args.awsAccountId:
    print("Setting private container registry for AWS account " + awsCloudAccount['awsCloudAccount']['accountName'])
    variables = {
      "input": {
        "exocomputeAccountId": awsCloudAccount['awsCloudAccount']['id'],
        "registryUrl": pcrFqdn,
        "pcrAwsImagePullDetails": {
          "awsNativeId": args.awsAccountId
        }
      }
    }

    try:
        setPrivateContainerRegistry = rubrik._query_raw(raw_query='mutation SetPrivateContainerRegistry($input: SetPrivateContainerRegistryInput!) {setPrivateContainerRegistry(input: $input)}',
                                          operation_name=None,
                                          variables=variables,
                                          timeout=60)
    except Exception as err:
        print("Error: Unable to set the private container registry.")
        print(err)
        sys.exit(1)

    print("Getting currently approved PCR bundle version numbers")
    variables = {
      "input": {
        "exocomputeAccountId": awsCloudAccount['awsCloudAccount']['id']
      }
    }

    try:
        privateContainerRegistry = rubrik._query_raw(raw_query='query PrivateContainerRegistry($input: PrivateContainerRegistryInput!) {privateContainerRegistry(input: $input) {pcrDetails {registryUrl imagePullDetails {... on PcrAwsImagePullDetails {awsNativeId}}} pcrLatestApprovedBundleVersion}}',
                                          operation_name=None,
                                          variables=variables,
                                          timeout=60)

    except Exception as err:
        print("Error: Unable to get the private container registry information for exocompute account: " + awsCloudAccount['awsCloudAccount']['accountName'])
        print(err)
        sys.exit(1)

    print("Current approved bundle version for AWS account " +  awsCloudAccount['awsCloudAccount']['accountName'] + "is: " + privateContainerRegistry['data']['privateContainerRegistry']['pcrLatestApprovedBundleVersion'])
# Get Exocompute Bundle (containers)

variables = {
  "input": {
    "eksVersion": args.eksVersion
  }
}

try:
    exoTaskImageBundle = rubrik._query_raw(raw_query='query ExotaskImageBundle { exotaskImageBundle {bundleVersion repoUrl bundleImages {name tag sha}}}',
                                      operation_name=None,
                                      variables=variables,
                                      timeout=60)
except Exception as err:
    print("Error: Unable to retrieve exotaskImageBundle")
    print(err)
    sys.exit(1)

logging.debug("")
logging.debug(json.dumps(exoTaskImageBundle, indent=2))
logging.debug("")

print("New bundle version is: " + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'])

# Exit if new bundle version is the same or lower than the current approved bundle version
if privateContainerRegistry['data']['privateContainerRegistry']['pcrLatestApprovedBundleVersion'] >= exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion']:
    print("New bundle version is the same or lower than the current approved bundle version. Exiting.")
    sys.exit(0)
    
region = exoTaskImageBundle['data']['exotaskImageBundle']['repoUrl'].split('.')[3]
print("")
print("Region: " + region)
rscRepoFqdn = exoTaskImageBundle['data']['exotaskImageBundle']['repoUrl']
print ("Repo URL: " + rscRepoFqdn)
pcrRegion= args.pcrFqdn.split('.')[3]
print("PCR Region: " + pcrRegion)
print("")


# Login to AWS ECR

rscEcrSession = boto3.Session()
rscEcrClient = rscEcrSession.client('ecr', region_name=region)

# Setup Docker client

dockerClient = docker.from_env()
docker_api_client = docker.APIClient(base_url='unix://var/run/docker.sock')

# Login to RSC ECR
# Requires that the RSC setPrivateContainerRegistry GraphQL mutation has been run to set the registry URL in RSC.
# This step would have been done as part of the RSC setup process.

# CLI example: "aws ecr get-login-password --region us-east-1 | docker login --username AWS --password-stdin <Rubrik_ECR_AWS_Account_ID>.dkr.ecr.us-east-1.amazonaws.com")

try:
    rscEcrToken = rscEcrClient.get_authorization_token(registryIds=[rscRepoFqdn.split('.')[0]])
except Exception as err:
    print("Error: Unable to get RSC ECR token.")
    print(err)
    sys.exit(1)

logging.info("rscEcrToken: %s", rscEcrToken)

try:
    username, password = base64.b64decode(rscEcrToken['authorizationData'][0]['authorizationToken']).decode('utf-8').split(":")
    rsc_auth_config_payload = { 'username': username, 'password': password }
    rscEcr = dockerClient.login(username=username, password=password, registry=rscEcrToken['authorizationData'][0]['proxyEndpoint'].replace("https://", ""), reauth=True)
except Exception as err:
    print("Error: Unable to login to RSC ECR")
    print(err)
    sys.exit(1)

# Pull images into local repository
for bundleImages in exoTaskImageBundle['data']['exotaskImageBundle']['bundleImages']:
    logging.info("rsc_auth_config_payload: %s", rsc_auth_config_payload)
    if bundleImages['tag']:
#       CLI example: "docker pull <Rubrik_ECR_AWS_Account_ID>.dkr.ecr.us-east-1.amazonaws.com/<build_image_name>:<tag>"
        print("Pulling " + bundleImages['name'] + " with tag " + bundleImages['tag'])
        try:
            for line in docker_api_client.pull(rscRepoFqdn + '/' + bundleImages['name'], tag=bundleImages['tag'], stream=True, auth_config=rsc_auth_config_payload, decode=True):
                print(line)
                logging.debug(json.dumps(line, indent=2))

        except Exception as err:
            print("Error: Image pull failed for " + bundleImages['name'] + " with tag " + bundleImages['tag'])
            print(err)
            sys.exit(1)
    elif bundleImages['sha']:
#       CLI example: "docker pull <Rubrik_ECR_AWS_Account_ID>.dkr.ecr.us-east-1.amazonaws.com/<build_image_name>@sha256:<sha>"
        print("Pulling " + bundleImages['name'] + " with sha " + bundleImages['sha'])
        try:
            for line in docker_api_client.pull(rscRepoFqdn + '/' + bundleImages['name'], tag="sha256:" + bundleImages['sha'], stream=True, auth_config=rsc_auth_config_payload, decode=True):
                print(line)
                logging.debug(json.dumps(line, indent=2))
        except Exception as err:
            print("Error: Image pull failed for " + bundleImages['name'] + " with sha " + bundleImages['sha'])
            print(err)
            sys.exit(1)
    else:
        print("Error: No tag or sha found for " + bundleImages['name'] + " in " + rscRepoFqdn + " bundle.")
        sys.exit(1)

# Scan images for vulnerabilities
print("")
print("Scanning images for vulnerabilities")

for bundleImages in exoTaskImageBundle['data']['exotaskImageBundle']['bundleImages']:
    if bundleImages['tag']:
        print("Scanning " + bundleImages['name'] + " with tag " + bundleImages['tag'])
        try:
            print("<Insert Image Scanning Tool Here>")
        except Exception as err:
            print("Error: Image scanning failed for " + bundleImages['name'] + " with tag " + bundleImages['tag'])
            print(err)
            sys.exit(1)
    elif bundleImages['sha']:
        print("Scanning " + bundleImages['name'] + " with sha " + bundleImages['sha'])
        try:
            print("<Insert Image Scanning Tool Here>")
        except Exception as err:
            print("Error: Image scanning failed for " + bundleImages['name'] + " with sha " + bundleImages['sha'])
            print(err)
            sys.exit(1)
    else:
        print("Error: No tag or sha found for " + bundleImages['name'] + " in " + rscRepoFqdn + " bundle.")
        sys.exit(1)
print("")

#Login to customer PCR on ECR if configured
if args.pcrAuth == "ECR":
  customerEcrSession = boto3.Session()
  customerEcrClient = customerEcrSession.client('ecr', region_name=pcrRegion)
  # Get customer PCR token
  # CLI Example "aws ecr get-authorization-token --region <customer_ecr_region>"
  try:
      customerEcrToken = customerEcrClient.get_authorization_token(registryIds=[pcrFqdn.split('.')[0]])
  except Exception as err:
      print("Error: Unable to get customer PCR token.")
      print(err)
      sys.exit(1)

    # CLI Example "aws ecr get-login-password --region <customer_ecr_region> | docker login --username AWS --password-stdin <customer_pcr_url>"
  try:
      username, password = base64.b64decode(customerEcrToken['authorizationData'][0]['authorizationToken']).decode('utf-8').split(":")
      customer_auth_config_payload = { 'username': username, 'password': password }
      customerEcr = dockerClient.login(username=username, password=password, registry=customerEcrToken['authorizationData'][0]['proxyEndpoint'].replace("https://", ""), reauth=True)
  except Exception as err:
      print("Error: Unable to login to customer PCR on ECR")
      print(err)
      sys.exit(1)
elif args.pcrAuth == "PWD":
    # Login to customer PCR on non ECR
    customer_auth_config_payload = { 'username': args.pcrUsername, 'password': args.pcrPassword }
    try:
        customerEcr = dockerClient.login(username=args.pcrUsername, password=args.pcrPassword, registry=pcrFqdn, reauth=True)
    except Exception as err:
        print("Error: Unable to login to customer PCR on non-ECR")
        print(err)
        sys.exit(1)

# Create Repos, Tag and push images to customer PCR

# Determine if repository exists and create if it does not.
# CLI example: "aws ecr describe-repositories --region <customer_ecr_region>"

for bundleImages in exoTaskImageBundle['data']['exotaskImageBundle']['bundleImages']:
    print("")
    if not pcrFqdn.partition('/')[2]:
        pcrRepoName = bundleImages['name']
    else:
        pcrRepoName = pcrFqdn.partition('/')[2] + '/' + bundleImages['name']
    logging.debug("pcrAuth is " + args.pcrAuth)
    if args.pcrAuth == "ECR":
        pcrRepositories = customerEcrClient.describe_repositories()
        repoExists = False
        logging.debug("PCR Repositories:")
        # logging.debug(pp.pprint(pcrRepositories))
        for repo in pcrRepositories['repositories']:
            logging.debug("repo name: " + repo['repositoryName'])
            logging.debug("bundleImages name:" + bundleImages['name'])
            if repo['repositoryUri'] == pcrFqdn + '/' + bundleImages['name']:
                print("Repository " + pcrFqdn + '/' + bundleImages['name'] + " already exists in " + pcrFqdn + ". Skipping create" )
                repoExists = True
                break
        # If repo does not exist, create it.
        if not repoExists:
            # CLI example: "aws ecr create-repository --repository-name <build_image_name> --region <customer_ecr_region> --image-scanning-configuration scanOnPush=true --encryption-configuration encryptionType=AES256 --image-tag-mutability IMMUTABLE"
            print("Creating repository: " + pcrRepoName)
            customerEcrClient.create_repository(repositoryName=pcrRepoName,
                                        imageScanningConfiguration={'scanOnPush': True},
                                        encryptionConfiguration={'encryptionType': 'AES256'},
                                        imageTagMutability='IMMUTABLE')

    if bundleImages['tag']:
        print("Tagging and pushing " + bundleImages['name'] + " with tag " + bundleImages['tag'] + " to " + pcrFqdn + '/' + bundleImages['name'] + " with version tag " + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'])
        # CLI Example "docker image tag <Rubrik_ECR_AWS_Account_ID>.dkr.ecr.us-east-1.amazonaws.com/<build_image_name>:<tag><customer_pcr_url>/<build_image_name>:<bundle_version>"
        try:
            docker_api_client.tag(rscRepoFqdn + '/' + bundleImages['name'] + ":" + bundleImages['tag'], pcrFqdn + '/' + bundleImages['name'] + ":" + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'])
        except Exception as err:
            print("Error: Image tag failed for " + bundleImages['name'] + " with tag " + bundleImages['tag'])
            print(err)
            sys.exit(1)
        print("Pushing " + bundleImages['name'] + " with tag " + bundleImages['tag'])

        # CLI Example "docker push <customer_pcr_url>/<build_image_name>:<bundle_version>"
        try:
            for line in docker_api_client.push(pcrFqdn + '/' + bundleImages['name'], tag=exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'], stream=True, auth_config=customer_auth_config_payload, decode=True):
                print(line)
                logging.debug(json.dumps(line, indent=2))
        except Exception as err:
            print("Error: Image push failed for " + bundleImages['name'] + " with tag " + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'])
            print(err)
            sys.exit(1)
    elif bundleImages['sha']:
        print("Tagging and pushing " + bundleImages['name'] + " with sha " + bundleImages['sha'] + " to " + pcrFqdn + '/' + bundleImages['name'] + " with version tag " + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'])
        # CLI Example "docker image tag <Rubrik_ECR_AWS_Account_ID>.dkr.ecr.us-east-1.amazonaws.com/<build_image_name>@sha256:<sha> <customer_pcr_url>/<build_image_name>:<bundle_version>"
        try:
            docker_api_client.tag(rscRepoFqdn + '/' + bundleImages['name'] + "@sha256:" + bundleImages['sha'], pcrFqdn + '/' + bundleImages['name'] +  ":" + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'])
        except Exception as err:
            print("Error: Image tag failed for " + bundleImages['name'] + " with sha " + bundleImages['sha'])
            print(err)
            sys.exit(1)
        print("Pushing " + bundleImages['name'] + " with sha " + bundleImages['sha'])

        # CLI Example "docker push <customer_pcr_url>/<build_image_name>:<bundle_version>"
        try:
            for line in docker_api_client.push(pcrFqdn + '/' + bundleImages['name'], tag=exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'], stream=True, auth_config=customer_auth_config_payload, decode=True):
                print(line)
                logging.debug(json.dumps(line, indent=2))
        except Exception as err:
            print("Error: Image push failed for " + bundleImages['name'] + " with sha " + bundleImages['sha'])
            print(err)
            sys.exit(1)

logging.debug(json.dumps(exoTaskImageBundle, indent=2))

#Accept Container Bundle
variables = {
  "input": {
    "approvalStatus": "ACCEPTED",
    "bundleVersion": "{}".format(exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion']),
    "bundleMetadata": {
        "eksVersion": args.eksVersion
    }
  }
}
SetBundleApprovalStatus = rubrik._query_raw(raw_query='mutation SetBundleApprovalStatus($input: SetBundleApprovalStatusInput!) {setBundleApprovalStatus(input: $input)}',
                                      operation_name=None,
                                      variables=variables,
                                      timeout=60)

logging.debug(json.dumps(exoTaskImageBundle, indent=2))

print()
print()
print("Bundle " + exoTaskImageBundle['data']['exotaskImageBundle']['bundleVersion'] + " has been accepted.")

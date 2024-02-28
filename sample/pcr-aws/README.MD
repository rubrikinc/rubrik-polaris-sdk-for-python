# Introduction

This script downloads the images that are used for Rubrik Security Cloud Exocompute on AWS. It provides an example for scanning these images and then pushing them to a Private Container Registry.

## Steps

1. [Download](https://www.python.org/downloads/) and [install](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python) Python 3
1. [Clone and install](https://github.com/rubrikinc/rubrik-polaris-sdk-for-python?tab=readme-ov-file#installation) the Rubrik Security Cloud Python SDK
1. Run `cd ../rubrik-polaris-sdk-for-python/sample/pcr-aws`
1. Run `pip3 install -r requirements.txt` to install the AWS Python Module and Docker Python Module.
1. [Create an RSC service account](https://docs.rubrik.com/en-us/saas/saas/adding_a_service_account.html) user and download the key file JSON file.
1. [Install the Docker engine](https://docs.docker.com/engine/install/).
1. Run `docker run hello-world` to verify that the Docker engine is working properly.
1. Make sure that you have enough space on your local system to download the images. Images will be downloaded to the default local Docker registry.
1. Run `python3 ./pcr.py --keyfile <path to keyfile> --pcrFqdn <FQDN_of_the_private_container_registry> --profile <Name_of_the_AWS_profile_with_the_private_container_registry>`
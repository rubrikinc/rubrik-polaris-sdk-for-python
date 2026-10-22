# Introduction

This script downloads the images that are used for Rubrik Security Cloud Exocompute on GCP. It provides an example for scanning these images and then pushing them to a Private Container Registry (Google Artifact Registry).

## Steps

1. [Download](https://www.python.org/downloads/) and [install](https://docs.python.org/3/using/unix.html#getting-and-installing-the-latest-version-of-python) Python 3
1. [Clone and install](https://github.com/rubrikinc/rubrik-polaris-sdk-for-python?tab=readme-ov-file#installation) the Rubrik Security Cloud Python SDK
1. Run `cd ../rubrik-polaris-sdk-for-python/sample/pcr-gcp`
1. Run `pip3 install -r requirements.txt` to install the required Python modules.
1. [Create an RSC service account](https://docs.rubrik.com/en-us/saas/saas/adding_a_service_account.html) and download the key file JSON.
1. [Install the Docker engine](https://docs.docker.com/engine/install/).
1. Run `docker run hello-world` to verify that the Docker engine is working properly.
1. Make sure that you have enough space on your local system to download the images. Images will be downloaded to the default local Docker registry.
1. Create a [GCP service account](https://cloud.google.com/iam/docs/service-accounts-create) that has:
   - Read access to Rubrik's Google Artifact Registry repository
   - Write access to your private Google Artifact Registry repository
1. [Download a JSON key file](https://cloud.google.com/iam/docs/keys-create-delete) for the GCP service account.
1. Ensure the GCP project is configured for Exocompute in RSC before running this script.
1. Run `python3 ./pcr.py --keyfile <path_to_rsc_keyfile> --gcpProjectNativeId <gcp_project_id> --gcpServiceAccountEmail <sa_email> --gcpSAKeyFile <path_to_gcp_sa_keyfile> --customerGarUrl <customer_gar_url>`. Add `--verbose` or `--debug` for more output.

The script registers the customer registry and GCP service account with RSC, pulls the latest Exocompute image bundle from Rubrik's registry, runs the (placeholder) image scan, pushes the images to the customer registry tagged with the bundle version, and finally approves the bundle in RSC. If the latest bundle version has already been approved, the script exits without pulling any images.

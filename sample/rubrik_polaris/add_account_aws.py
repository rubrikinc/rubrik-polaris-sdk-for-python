from rubrik_polaris import PolarisClient


domain = 'my-company'
username = 'john.doe@example.com'
password = 's3cr3tP_a55w0R)'


client = PolarisClient(domain, username, password, insecure=True)
success = client.add_account_aws(regions=["us-west-2"], all=True)
if success:
    print("AWS Account added successfully!")

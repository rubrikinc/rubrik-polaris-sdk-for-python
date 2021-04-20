from rubrik_polaris import PolarisClient


domain = 'my-company'
username = 'john.doe@example.com'
password = 's3cr3tP_a55w0R)'
cluster_id = '602909f2-q330-4da9-9389-911d66abb529'


client = PolarisClient(domain, username, password, insecure=True)

cluster_location = client.get_cdm_cluster_location(cluster_id)

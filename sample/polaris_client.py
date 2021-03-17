#! /usr/bin/env python3
import argparse
import pprint
import sys
import rubrik_polaris
import datetime


pp = pprint.PrettyPrinter(indent=4)

parser = argparse.ArgumentParser()
parser.add_argument('-p', '--password', dest='password', help="Polaris Password", default=None)
parser.add_argument('-u', '--username', dest='username', help="Polaris UserName", default=None)
parser.add_argument('-d', '--domain', dest='domain', help="Polaris Domain", default=None)
parser.add_argument('-r', '--root', dest='root_domain', help="Polaris Root Domain", default=None)
parser.add_argument('--insecure', help='Deactivate SSL Verification', action="store_true")

args = parser.parse_args()

try:
    rubrik = rubrik_polaris.PolarisClient(args.domain, args.username, args.password, root_domain=args.root_domain,
                                          insecure=args.insecure)
except Exception as err:
    print(err)
    sys.exit(1)

### Add GCP Project
# rubrik.add_project_gcp(service_account_auth_key_file="/home/peterm/.google.milanese.json", gcp_native_project_id="home-network-274622")

### Delete GCP Project
# rubrik.delete_project_gcp(gcp_native_project_id="home-network-274622")

### Add AWS Acct (local profile must be configured, specify list of profiles _or_ set all=True.
# rubrik.add_account_aws(regions = ["us-east-1"], profiles = ["milanese"])
# rubrik.add_account_aws(regions = ["us-east-1"], aws_access_key_id='blah', aws_secret_access_key='blah')
# rubrik.add_account_aws(regions = ["us-west-2"], all = True )

### Remove AWS Acct (local profile must be configured, specify list of profiles _or_ set all=True.
# rubrik.delete_account_aws(profiles = ['milanese'])
# rubrik.delete_account_aws(aws_access_key_id='blah', aws_secret_access_key='blah')
# rubrik.delete_account_aws(all = True )

### Run ODS for machines in a region using Bronze retention, monitor to complete via threads
# bronze_sla_domain_id = rubrik.get_sla_domains("Bronze")['id']
# pp.pprint(rubrik.submit_on_demand(rubrik.get_compute_object_ids_azure(region="EastUS2"), bronze_sla_domain_id, wait=True))

### Get snapshot ids for snappables
# snappables = rubrik.get_compute_object_ids_ec2(tags={"Name": "gurlingjb"})
# snappables = rubrik.get_compute_object_ids_azure(name = "tpm1-lin1")
# snappables = rubrik.get_compute_object_ids_gce(nativeName = "ubuntu-fdse-shared-1")
# for snappable in snappables:
#     snapshot_id = (rubrik.get_snapshots(snappable, recovery_point='latest')['id']) # can include anything up to this. 2020 is ok, 2020-09, 2020-09-19, ...
#     snapshot_id = rubrik.get_snapshots(snappable, recovery_point='latest')
#     pp.pprint(rubrik.get_snapshots(snappable)) # Get all snapshots
#     pp.pprint(snapshot_id)

### Submit Restore for above Snapshot (EC2)
#     result = rubrik.submit_compute_restore_ec2(snapshot_id, wait=True, should_power_on=True, should_restore_tags=True)
#     result = rubrik.submit_compute_restore_azure(snapshot_id, wait=True, should_power_on=True, should_restore_tags=True)
#     result = rubrik.submit_compute_restore_gce(snapshot_id, wait=True, should_power_on=True, should_restore_tags=True)
#     pp.pprint(result)

### Query objects, set sla_domain
# gold_sla_domain_id = rubrik.get_sla_domains("Gold")['id']
# object_ids = rubrik.get_compute_object_ids_ec2(instanceName="tm2-aws-w1")
# pp.pprint(rubrik.submit_assign_sla(object_ids=object_ids, sla_id=gold_sla_domain_id))
# pp.pprint(rubrik.submit_assign_sla(object_ids=object_ids, global_sla_assign_type="doNotProtect", existing_snapshot_retention="KEEP_FOREVER"))

### Manipulate AWS EBS Volumes
# pp.pprint(rubrik.get_storage_ebs())
# rubrik.get_object_ids_ebs(tags = {"Class": "Management"})
# bronze_sla_domain_id = rubrik.get_sla_domains("Bronze")['id']
# pp.pprint(rubrik.submit_on_demand(rubrik.get_object_ids_ebs(volumeId = "vol-077d1df3538afe5dd"), bronze_sla_domain_id, wait=True))

### Returns all objectIDs matching arbitrary available inputs. ec2 tags have special treatment
# pp.pprint(rubrik.get_compute_object_ids_ec2(tags = {"Name": "Puppet Master"}))
# pp.pprint(rubrik.get_compute_object_ids_azure(region = "EastUS2"))
# pp.pprint(rubrik.get_compute_object_ids_gce(region = "us-west1"))

### Search for a set of objects and get their details
# for i in rubrik.get_compute_object_ids_ec2(region = 'US_WEST_2'):
#     pp.pprint(rubrik.get_compute_ec2(i))

### Returns all instances
# pp.pprint(rubrik.get_compute_ec2())
# pp.pprint(rubrik.get_compute_gce())
# pp.pprint(rubrik.get_compute_azure())

### Returns sla domain map, or specified name/id
# pp.pprint(rubrik.get_sla_domains())
# pp.pprint(rubrik.get_sla_domains("Bronze"))

### Returns specified cloud account details, or all
# pp.pprint(rubrik.get_accounts_aws("gurling"))
# pp.pprint(rubrik.get_accounts_aws_detail(""))
# pp.pprint(rubrik.get_accounts_gcp("Trinity-FDSE"))
# pp.pprint(rubrik.get_accounts_azure("RubrikRangers"))
# pp.pprint(rubrik.get_accounts_aws())
# pp.pprint(rubrik.get_accounts_gcp())
# pp.pprint(rubrik.get_accounts_azure())
# pp.pprint(rubrik.update_account_aws())

### Event interface
# end_time = datetime.datetime.now().isoformat()
# start_time = (datetime.datetime.now() - datetime.timedelta(days=1)).isoformat()
# todays_failed_events = rubrik.get_event_series_list(cluster_ids=['603109f2-eb30-4da8-9389-911d66abb524'], status=["Failure"], start_time=start_time, end_time=end_time)
# todays_failed_events = rubrik.get_event_series_list(activity_type=["Hardware"], start_time=start_time, end_time=end_time)
# print("Returned events : {}".format(len(todays_failed_events)))

### Basic event summaries
# summary = {}
# for event in todays_failed_events:
#     if event['lastActivityType'] in summary:
#         summary[event['lastActivityType']] += 1
#     else:
#         summary[event['lastActivityType']] = 1
# pp.pprint(summary)

# Summarize further
# summary = {}
# for event in todays_failed_events:
#     if event['objectType'] in summary:
#         if event['location']:
#             second_level = "{} : {}".format(event['location'], event['objectName'])
#         else:
#             second_level = event['objectName']
#         if second_level in summary[event['objectType']]:
#             summary[event['objectType']][second_level] += 1
#         else:
#             summary[event['objectType']][second_level] = 1
#     else:
#         summary[event['objectType']] = {}
# pp.pprint(summary)

### Get accepted ENUM values
# pp.pprint(rubrik.get_enum_values(name="ExistingSnapshotRetentionEnum"))

### Get Report Data
# report_data = rubrik.get_report_data()

### Basic report summaries
# summary = {}
# for object in report_data:
#     if object['objectType'] in summary:
#         summary[object['objectType']] += 1
#     else:
#         summary[object['objectType']] = 1
# pp.pprint(summary)

### Export ec2 to another region
# pp.pprint(rubrik.submit_compute_export_ec2(
#     snapshot_id='5d932b7d-6c12-4efb-b3f7-d79beddf655a',
#     aws_account_number='880059949679',
#     aws_region='EU_WEST_2',
#     aws_vpc='vpc-d56f3bbd',
#     aws_security_groups=['sg-ca5d01ad'],
#     aws_subnet='subnet-bbe44cf7',
#     wait=True
# ))

### Check for duplicate vms
# vms = rubrik.get_compute_vsphere()
# o = {}
# for vm in vms:
#     print('.', end="")
#     if vm['name'] in o and not vm['isRelic']:
#         o[vm['name']].append(vm['cluster']['name'])
#     elif not vm['isRelic']:
#         o[vm['name']] = [vm['cluster']['name']]
# for vm in o:
#     if len(o[vm]) > 1:
#         print("{} : {}".format(vm, o[vm]))
#! /usr/bin/env python3
import datetime
import os
import pprint
import sys

# Add the directory containing `polaris_client.py` to sys.path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from polaris_client import build_arg_parser, create_polaris_client

pp = pprint.PrettyPrinter(indent=4)


def get_todays_failed_events(client, cluster_ids=None):
    """Fetch and return today's failed events for the passed clusters."""
    end_time = datetime.datetime.now().isoformat()
    start_time = (datetime.datetime.now() - datetime.timedelta(
        days=1)).isoformat()
    return rubrik.get_event_series_list(cluster_ids=cluster_ids,
                                        status=["FAILURE"],
                                        start_time=start_time,
                                        end_time=end_time)


if __name__ == "__main__":
    parser = build_arg_parser()
    parser.add_argument('-f', '--first', dest='first',
                        help="Number of clusters to get events for",
                        default=1, type=int)
    args = parser.parse_args()
    rubrik = create_polaris_client(args)

    clusters = rubrik.list_clusters(first=args.first)
    ids = [cluster['id'] for cluster in clusters]
    if len(ids) == 0:
        print("No clusters found.")
        sys.exit(0)
    # workaround for bug in list_clusters not honoring first=1
    ids = ids[:args.first]
    print("Found {} cluster(s): {}".format(len(ids), ids))
    events = get_todays_failed_events(rubrik, ids)
    print("Returned events : {}".format(len(events)))
    if len(events) > 0:
        print("Event 0 : {}".format(events[0]))

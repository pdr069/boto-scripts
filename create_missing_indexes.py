#!/usr/bin/env python
import os
import sys
import argparse
import time
import datetime
import uuid

# Colored printing for terminal output.
from termcolor import colored

# Boto specific imports.
import boto
from boto.dynamodb2.layer1 import DynamoDBConnection
from boto.dynamodb2.table import Table

def db_connection(config_path='~/.aws/credentials', region='us-west-2',
        instance='default'):
    """
    This method does regional DynamoDBConnection.
    """
    # Define the aws credentials file.
    boto.config.read(os.path.expanduser(config_path))

    # Grab the access and secret keys from the credentials file.
    ak = boto.config.get(instance, 'aws_access_key_id')
    sk = boto.config.get(instance, 'aws_secret_access_key')

    # Set the region to perform queries.
    DynamoDBConnection.DefaultRegionName = region

    # Return the actual DynamoDB connection object.
    return DynamoDBConnection(aws_access_key_id=ak,
       aws_secret_access_key = sk)


def create_missing_indexes(m_region, r_region, instance):
    # Skip all DynamoDB metadata tables.
    master_tables = [ i for i in db_connection(region=m_region).list_tables()['TableNames'] if i.startswith('DynamoDB') is False ]

    # Main db diff loop, just global indexes.
    for m1 in master_tables:
        # Set the region before selecting the table to describe.
        DynamoDBConnection.DefaultRegionName = m_region
        t = Table(m1)
        t.describe()

        # Set replica region to get table information.
        DynamoDBConnection.DefaultRegionName = r_region

        try:
            s = Table(m1)
            s.describe()
        except boto.exception.JSONResponseError:
            print colored("!!! CREATE TABLE '{0}' table doesn't exist in '{1}' region. ".format(m1, r_region), "red")
            # raise SystemExit("Ensure table exists in replica region and re-run.", 1)

        if len(t.global_indexes) > 0:
            print colored('{0} has globlal indexes.'.format(m1), 'green')
            # Get destination table global index names.
            d_index_names = [ i.schema()['IndexName'] for i in s.global_indexes ]

            # Check if any global indexes exist in replica table prior to trying
            # to create them and skip them if they do exist.
            for index in t.global_indexes:
                if index.schema()['IndexName'] in d_index_names:
                    print "Index '{0}' exists in replica, skipping.".format(index.schema()['IndexName'])
                    continue
                else:
                    print "\tCreating '{0}' index in replica table.".format(index.schema()['IndexName'])
                    for retry_count in range(0, 6):
                        try:
                            if s.create_global_secondary_index(index) is True:
                                print colored("Successfully created index '{0}' on '{1}' table.".format(index.schema()['IndexName'], s.table_name), "green")
                                break
                            else:
                                print colored("Failed to create index '{0}' on '{1}' table.".format(index.schema()['IndexName'], s.table_name), "red")
                        except boto.exception.JSONResponseError:
                            print "Index creation is finishing up, sleeping 1 minute before proceeding."
                            time.sleep(60)
                            continue
                    else:
                        print colored("!!! Retry count exceeded!  Manually create '{0}' index.".format(index.schema()['IndexName']), "red")
        else:
            print colored('{0} has no global indexes.  Skipping table.'.format(m1), 'red')

    print "Index creation complete."


if __name__ == "__main__":
    master_region = 'us-west-2'
    replica_region_1 = 'us-east-1'
    replica_region_2 = 'ap-northeast-1'
    profile = 'default'
    create_missing_indexes(master_region, replica_region_1, profile)
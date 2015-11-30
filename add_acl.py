#!/usr/bin/env python
import os
import sys
import uuid
import time
import datetime
import argparse

# boto specific imports.
import boto.vpc as vpc

# Global dictionary skeleton to use.
rule = {
    'network_acl_id' : None,
    'rule_number' : None,
    'protocol' : -1,
    'rule_action' : u'deny',
    'cidr_block' : None,
    'egress' : False,
    'icmp_type' : -1,
    'icmp_code' : -1,
    'port_range_from' : 1,
    'port_rage_to' : 65535
}




def main(access_key, secret_key, path, region, instance, cidr, protocol, icmp_type,
    icmp_code, start_port, end_port, vpc_id, rule_number):
    """
    Parse inputs and apply rule to black list all traffic from <cidr>.
    """
    conn = None

    if access_key is None or secret_key is None:
        conn = vpc.connect_to_region(region)
    else:
        conn = vpc.connect_to_region(region=region, **{'aws_access_key_id' : access_key,
            'aws_secret_access_key' : secret_key})

    if conn is None:
        print "Unable to connect to region with credentials."
        raise SystemExit(1)

    print "\nConnection: {0}\n".format(conn)

    rule['rule_number'] = rule_number
    rule['protocol'] = protocol
    rule['cidr_block'] = cidr
    rule['icmp_type'] = icmp_type
    rule['icmp_code'] = icmp_code
    rule['port_range_from'] = start_port
    rule['port_range_to'] = end_port

    print rule

    if protocol == 'list':
        vpcs = conn.get_all_vpcs()
        for i in vpcs:
            try:
                print i, i.tags['Name'], i.cidr_block
            except:
                print i, 'No Tags Available', i.cidr_block

    conn.close()
    raise SystemExit(0)



if __name__ == "__main__":
    # Setup command line arguments (add additional parameter(s) here).
    parser = argparse.ArgumentParser(description="%(prog)s: Input parameters for black listing.")
    parser.add_argument('-A', '--access-key', default=None, help="AWS access key id.")
    parser.add_argument('-S', '--secret-key', default=None, help="AWS secret access key.")
    parser.add_argument('-p', '--path', default='~/.aws/credentials', help="Path to credentials file.")
    parser.add_argument('-r', '--region', default='us-west-2', help="AWS regiong to connect to.")
    parser.add_argument('-i', '--instance', default='default', help="Instance in credential file to use.")
    parser.add_argument('-c', '--cidr', default=None, help="CIDR block to black list.")
    parser.add_argument('-P', '--protocol', default=-1, help="Type of protocol to block (default is all).")
    parser.add_argument('-I', '--icmp-type', default=-1, help="ICMP type to block (default is all).")
    parser.add_argument('-C', '--icmp-code', default=-1, help="ICMP code to block (default is all).")
    parser.add_argument('-s', '--start-port', default=0, help="Port range starting point (default is 0).")
    parser.add_argument('-e', '--end-port', default=65535, help="Port range ending point (default is 65535).")
    parser.add_argument('-v', '--vpc-id', default=None, help="VPC id to ACL to.")
    parser.add_argument('-R', '--rule-number', default=32767, help="Rule number (1-32767), default is 32767.")
    parser.add_argument('-l', '--list', default=1, help="List available vpcs.")

    args = parser.parse_args()
    
    if args.list:
        args.protocol='list'
        main(access_key=args.access_key, secret_key=args.secret_key, path=args.path, region=args.region, 
            instance=args.instance, cidr=args.cidr, protocol=args.protocol, icmp_type=args.icmp_type, 
            icmp_code=args.icmp_code, start_port=args.start_port, end_port=args.end_port, vpc_id=args.vpc_id,
            rule_number=args.rule_number)
    elif args.vpc_id is not None and args.cidr is not None:
        main(access_key=args.access_key, secret_key=args.secret_key, path=args.path, region=args.region, 
            instance=args.instance, cidr=args.cidr, protocol=args.protocol, icmp_type=args.icmp_type, 
            icmp_code=args.icmp_code, start_port=args.start_port, end_port=args.end_port, vpc_id=args.vpc_id,
            rule_number=args.rule_number)
    else:
        parser.print_help()

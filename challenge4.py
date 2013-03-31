#!/usr/bin/env python

import argparse
import os
import pyrax
import re
import sys

def getDomain(fqdn):
    if not re.search('^(\w+\.)+$', fqdn + '.'):
        print "Invalid FQDN: %s" % fqdn
        sys.exit(1)
    domainname = fqdn
    while domainname.count('.') > 1:
        domainname = domainname[domainname.find('.') + 1:]
        try:
            domain = dns.find(name=domainname)
        except pyrax.exceptions.NotFound:
            #print "Failed attempting using %s as domain." % domainname
            pass
        else:
            #print "Domain found!, using %s" % domainname
            return domainname
    print "No domain was found for the fqdn provided."
    sys.exit(1)

def validateIPv4(ip):
    if not re.search('^((25[0-5]|2[0-4]\d|[01]?\d\d?)\.){4}$', ip + '.'):
        print "Invalid IP: %s" % ip
        sys.exit(1)
    return ip

def addRecord(fqdn, ip, type='A', ttl=300):
    domainname = getDomain(fqdn)
    domain = dns.find(name=domainname)
    rec = {"type": type,
           "name": fqdn,
           "data": ip,
           "ttl": ttl}
    if domain.search_records('A', name=fqdn, data=ip):
        print "Record already in place"
        sys.exit(1)
    try:
        dns.add_records(domain, rec)
    except pyrax.exceptions.DomainRecordAdditionFailed:
        print "Failed adding %s to %s domain." % (fqdn, domainname)
        sys.exit(1)
    else:
        print "Record successfully Added!"

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='CloudDNS. A Record Creation.')
    parser.add_argument('--fqdn', metavar='FQDN', required=True,
                        help='FQDN to add as an A Record.')
    parser.add_argument('--ip', metavar='IPV4', required=True,
                        help='IPv4 to use on the A Record.')
    args = parser.parse_args()

    creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
    pyrax.set_credential_file(creds_file)
    dns = pyrax.cloud_dns

    if not args.fqdn or not args.ip: 
        parser.print_help()
        sys.exit(1)

    addRecord(args.fqdn,validateIPv4(args.ip))
    sys.exit(0)

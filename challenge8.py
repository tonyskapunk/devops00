#!/usr/bin/env python

import argparse
import auth
import re
import sys
from challenge3 import *
from challenge4 import *
from pyrax import cloudfiles as cf

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cloud File Creator.')
    parser.add_argument('-c', '--container', metavar='NAME',
                        help='Container name')
    parser.add_argument('-f', '--fqdn', metavar='FQDN', required=True,
                        help='Name to use as CNAME.')
    parser.add_argument('-l', '--list-containers', action='store_true',
                        help='Prints the available containers of Cloud Files')
    args = parser.parse_args()

    if args.list_containers:
        listContainers()

    container = randomStr(8) if not args.container else args.container
    if not isContainer(container):
        print "Creating container: %s" % (container)
        cont = cf.create_container(container)
    else:
        print "Container %s already in place." % (container)
        cont = cf.get_container(container)
    # enable Static Website on container
    cf.set_container_web_index_page(container, 'index.html')
    # Activate CDN
    cont.make_public(ttl=600)
    index = """<html>\n<head>\n<title>Challenge 8\n</title>\n</head>\n<body>
<h1>Challenge 8</h1>\nfoo bar baz\n</body>\n</html>"""
    # Upload object
    obj = cf.store_object(container, 'index.html', index)
    cdn_uri = re.sub('http://', '', cont.cdn_uri)
    # Add CNAME
    addRecord(args.fqdn, cdn_uri, type='CNAME')
    print "Visit your site at: http://%s" % args.fqdn
    sys.exit(0)

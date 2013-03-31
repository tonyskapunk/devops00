#!/usr/bin/env python

import argparse
import os
import pyrax
import re
import sys
import time

def listContainers():
    print "Available Containers:"
    for container in cf.list_containers():
        print "%s" % (container)
    print cf.get_all_containers()
    sys.exit(0)

def isContainer(container):
    ret = False
    for cont in cf.list_containers():
        if cont == container:
            ret = True
            break
    return ret
        
def randomStr(length):
    return re.sub('\W','',os.urandom(200))[:length]
if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cloud File CDN Creator.')
    parser.add_argument('-c', '--container', metavar='NAME', 
                        help='Container name to make public via CDN.')
    parser.add_argument('-l', '--list-containers', action='store_true',
                        help='Prints the available containers of Cloud Files')
    args = parser.parse_args()

    creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
    pyrax.set_credential_file(creds_file)
    cf = pyrax.cloudfiles


    if args.list_containers:
        listContainers()

    container = randomStr(8) if not args.container else args.container
    if not isContainer(container):
        print "Creating container: %s" % (container)
        cont = cf.create_container(container)
    else:
        print "Container %s already in place." % (container)
        cont = cf.get_container(container)

    cont.make_public(ttl=600)
    print "%s\n%s\n%s\n" % (cont.cdn_uri, cont.cdn_ssl_uri, cont.cdn_streaming_uri)
    sys.exit(0)

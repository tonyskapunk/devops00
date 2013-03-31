#!/usr/bin/env python

import auth
import argparse
import os
from pyrax import cloudfiles
import re
import sys
import time

def listContainers():
    print "Available Containers:"
    for container in cloudfiles.list_containers():
        print "%s" % (container)
    print cloudfiles.get_all_containers()
    sys.exit(0)

def isContainer(container):
    ret = False
    for cont in cloudfiles.list_containers():
        if cont == container:
            ret = True
            break
    return ret
        
def randomStr(length):
    return re.sub('\W','',os.urandom(200))[:length]

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cloud File Creator.')
    parser.add_argument('-c', '--container', metavar='NAME',
                        help='Container name')
    parser.add_argument('-d', '--directory', metavar='PATH',
                        help='Local directory to upload')
    parser.add_argument('-l', '--list-containers', action='store_true',
                        help='Prints the available containers of Cloud Files')
    args = parser.parse_args()

    if args.list_containers:
        listContainers()

    if args.directory:
        dir = args.directory
    else:
        print "A directory (-d/--directory) is required."
        sys.exit(1)
    if not os.path.exists(dir):
        print "%s: is not a valid directory." % (dir)
        sys.exit(1)

    container = randomStr(8) if not args.container else args.container
    if not isContainer(container):
        print "Creating container: %s" % (container)
        cont = cloudfiles.create_container(container)
    else:
        print "Container %s already in place." % (container)

    upload_key, bytes = cloudfiles.upload_folder(dir, container)
    uploaded = 0
    print "Uploading %s bytes." % (bytes)
    while uploaded < bytes:
        uploaded = cloudfiles.get_uploaded(upload_key)
        print "\r%4.2f%% Completed." % ((uploaded * 100.0) / bytes)
        time.sleep(2)
    sys.exit(0)

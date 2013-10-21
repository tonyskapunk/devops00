#!/usr/bin/env python

import auth
import argparse
import os
import sys
import time
from pyrax import cloudfiles
from challenge1 import randomStr

def listContainers():
    print "Available Containers:"
    for container in cloudfiles.list_containers():
        print "%s" % (container)
    #print cloudfiles.get_all_containers()

def isContainer(container):
    ret = False
    for cont in cloudfiles.list_containers():
        if cont == container:
            ret = True
            break
    return ret

def listFiles(container):
    pr = False
    objs = cloudfiles.get_container_objects(container, full_listing=True)
    if len(objs) > 100:
        print "Found %s files, do you reallly want to continue [y/N]?" % len(objs)
        ans = raw_input()
        if ans.lower()[0] == 'y':
           pr = True
    else:
        pr = True
    if pr:    
        for obj in objs:
            print "%s" % (obj.name)
    sys.exit(0)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cloud File Creator.')
    parser.add_argument('-c', '--container', metavar='NAME',
                        help='Container name')
    parser.add_argument('-d', '--directory', metavar='PATH',
                        help='Local directory to upload')
    parser.add_argument('-l', '--list-containers', action='store_true',
                        help='Prints the available containers of Cloud Files')
    parser.add_argument('-f', '--list-files', action='store_true',
                        help='Prints the available files in a container')
    args = parser.parse_args()

    if args.list_containers:
        listContainers()
        sys.exit(0)
    if args.list_files:
        if isContainer(args.container):
            listFiles(args.container)
        else:
            print "Invalid Container: %s" % (args.container)
            sys.exit(1)
        sys.exit(0)

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

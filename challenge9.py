#!/usr/bin/env python

import argparse
import auth
import re
import sys
from challenge1 import *
from challenge4 import *

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cloud Sever+FQDN Creator.')
    parser.add_argument('--fqdn', metavar='FQDN', required=True,
                        help='Name to use as A record for the Cloud Server.')
    parser.add_argument('-F', '--flavor-list', action='store_true',
                        help='Prints the available Server Flavors/Sizes.')
    parser.add_argument('-f', '--flavor', metavar='SIZE', default=512, type=int,
                        help='Size to use on servers. Default 512.')
    parser.add_argument('-I', '--image-list', action='store_true',
                        help='Prints the available Server Images.')
    parser.add_argument('-i', '--image', metavar='IMG_NAME', default='arch',
                        help='Name of Image to use(first match). Default Arch.')
    args = parser.parse_args()
    
    if args.flavor_list:
        flavorList()
        sys.exit(0)

    if args.image_list:
        imageList()
        sys.exit(0)

    if not isValidImage(args.image):
        print "Invalid Image: %s" % (args.image)
        sys.exit(1)

    if not isValidFlavor(args.flavor):
        print "Invalid Flavor: %s" % (args.flavor)
        sys.exit(1)

    if not args.fqdn: 
        parser.print_help()
        sys.exit(1)

    domainname = getDomain(args.fqdn)
    print "Serving your request, please wait..."
    flavor = getFlavor(args.flavor)
    image = getImage(args.image)
    servers = createServers(1, args.fqdn, image, flavor)
    s = servers[0]
    addRecord(args.fqdn, s.accessIPv4)
    print "Now you can connect using: ssh root@%s" % args.fqdn
    sys.exit(0)

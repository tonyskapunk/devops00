#!/usr/bin/env python

import argparse
import os
import pyrax
import time
import sys

def imageList():
     print "Available Images:"
     for img in cs.images.list():
          print img.name.lower()

def flavorList():
     print "Available Flavors:"
     for flv in cs.flavors.list():
          print flv.ram

def getFlavor(flavorname):
     return [flv for flv in cs.flavors.list() if flv.ram == flavorname][0]

def getImage(imagename):
     return [img for img in cs.images.list() if imagename in img.name.lower()][0]

def isValidImage(image):
    for img in cs.images.list():
         if str(image).lower() in img.name.lower():
              return True
    return False

def isValidFlavor(flavor):
    for flv in cs.flavors.list():
         if flv.ram == flavor:
              return True
    return False

def createServers(count, name, image, flavor):
     servers = []
     srvs = []
     delay = 5
     build_time = 240 + delay * count
     for index in range(count):
          tmp_srv = cs.servers.create("%s%s" % (name, index), image, flavor)
          servers.append(tmp_srv)
     print "Building Servers. Might take about  %s secs..." % (build_time)
     time.sleep(build_time)
     servertime = build_time
     while True:
          if not servers:
               break
          s = servers[0]
          del servers[0]
          s.get()
          if s.status == 'ACTIVE':
               if s.networks:
                    public = s.networks['public']
                    if ":" in public[0]:
                         publicv4 = public[1]
                    else:
                         publicv4 = public[0]
                    print "%s: %s / %s" % (s.name, publicv4, s.adminPass)
                    srvs.append(s)
               else:
                    print "Server is Active but no network info found yet."
          elif s.status == "ERROR":
               print "Alas! something went wrong, rebuilding %s." % s.name
               s.delete()
               s = cs.servers.create(s.name, image, flavor)
               servers.append(s)
          else:
               servers.append(s)
          time.sleep(delay)
     return srvs

if __name__ == '__main__':
     parser = argparse.ArgumentParser(description='Cloud Server Creator.')
     parser.add_argument('-F', '--flavor-list', action='store_true',
                         help='Prints the available Server Flavors/Sizes.')
     parser.add_argument('-f', '--flavor', metavar='SIZE', default=512, type=int,
                         help='Size to use on servers. Default 512.')
     parser.add_argument('-I', '--image-list', action='store_true',
                         help='Prints the available Server Images.')
     parser.add_argument('-i', '--image', metavar='IMG_NAME', default='arch',
                         help='Name of Image to use(first match). Default Arch.')
     parser.add_argument('-n', '--number', metavar='COUNT', default=3, type=int,
                         help='Number of Servers, default 3')
     parser.add_argument('-s', '--server-prefix', metavar='NAME',
                         help='Prefix name for the Cloud Servers.')
     args = parser.parse_args()

     creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
     pyrax.set_credential_file(creds_file)
     cs = pyrax.cloudservers

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

     print "Serving your request, please wait..."
     flavor = getFlavor(args.flavor)
     image = getImage(args.image)
     sname = 'x' + args.server_prefix if args.server_prefix else randomStr(8)
     servers = createServers(args.number, sname, image, flavor)
     sys.exit(0)

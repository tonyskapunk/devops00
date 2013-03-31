#!/usr/bin/env python

import argparse
import auth
import sys
import time
from pyrax import cloudservers as cs
from challenge1 import *

if __name__ == "__main__":
     parser = argparse.ArgumentParser(description='Cloud Server Clone.')
     parser.add_argument('-F', '--flavor-list', action='store_true',
                         help='Prints the available Server Flavors/Sizes.')
     parser.add_argument('-f', '--flavor', metavar='SIZE', default=512, type=int,
                         help='Size to use on servers. Default 512.')
     parser.add_argument('-I', '--image-list', action='store_true',
                         help='Prints the available Server Images.')
     parser.add_argument('-i', '--image', metavar='IMG_NAME', default='arch',
                         help='Name of Image to use(1st match). Default Arch.')
     parser.add_argument('-s', '--server-name', metavar='NAME',
                         help='Server Name for the *cloned* Cloud Server.')
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

     print "Serving your request, please wait..."
     flavor = getFlavor(args.flavor)
     image = getImage(args.image)
     sname = 'x' + randomStr(8)
     img_name = randomStr(8)

     servers = createServers(1, sname, image, flavor)
     s = servers[0]
     img_id = s.create_image(img_name)
     while True:
          s.get()
          # While building this attr is set to 'image_snapshot'
          if s.__getattr__('OS-EXT-STS:task_state'):
               time.sleep(5)
          else:
               print "Deleting original server."
               s.delete()
               break
     print "Creating a clone server from image created"
     cimage = getImage(img_name)
     createServers(1, args.server_name, cimage, flavor)
     sys.exit(0)

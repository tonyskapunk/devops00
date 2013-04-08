#!/usr/bin/env python

import argparse
import auth
import os
from pyrax import cloudfiles as cf
import re
import sys
import time
from challenge1 import *
from challenge3 import *
from challenge4 import *
from challenge7 import *

def uploadFile(text, name, cointainer):
     if not isContainer(container):
          cont = cf.create_container(container)
     else:
          cont = cf.get_container(container)
     obj = cf.store_object(container, name, text)
     cont.make_public(ttl=600)
     print "%s/%s" % (cont.cdn_uri, name)

if __name__ == '__main__':
     parser = argparse.ArgumentParser(description='--- Challenge 10 ---')
     parser.add_argument('-a', '--algorithm', metavar='ALGORITHM', 
                         default='round_robin',
                         help='Algorithm to use in the LB. Default round_robin')
     parser.add_argument('-A', '--algorithm-list', action='store_true',
                         help='Prints the supported algorithms.')
     parser.add_argument('-F', '--flavor-list', action='store_true',
                         help='Prints the available Server Flavors/Sizes.')
     parser.add_argument('-f', '--flavor', metavar='SIZE', default=512,
                         type=int, help='Size to use on servers. Default 512.')
     parser.add_argument('--fqdn', metavar='FQDN',
                         help='FQDN to add as an A Record for the LB.')
     parser.add_argument('-I', '--image-list', action='store_true',
                         help='Prints the available Server Images.')
     parser.add_argument('-i', '--image', metavar='IMG_NAME', default='arch',
                         help='Name of Image to use(1st match). Default Arch.')
     parser.add_argument('--lbname', metavar='NAME', help='Name for the LB.')
     parser.add_argument('-n', '--node-count', metavar='COUNT', default=2,
                         type=int, 
                         help='Number of Servers behind the LB, default 2')
     parser.add_argument('-p', '--port', metavar='PORT', default=80, type=int,
                         help='Port number to use in the LB. Default 80')
     parser.add_argument('--port-on-nodes', metavar='PORT', default=80,
                         type=int,
                         help='Port number to use on the nodes. Default 80.')
     parser.add_argument('--protocol', metavar='PROTOCOL', default='http',
                         help='Protocol to use in the Cloud LB. Default http')
     parser.add_argument('--protocol-list', action='store_true',
                         help='Prints the supported protocols.')
     parser.add_argument('-s', '--server-prefix', metavar='NAME',
                         help='Prefix name for the Cloud Servers.')
     parser.add_argument('--ssh-key', metavar='FILENAME',
                         help='Filename of the ssh public key.')
     args = parser.parse_args()
     
     if args.flavor_list:
          flavorList()
          sys.exit(0)

     if args.image_list:
          imageList()
          sys.exit(0)

     if args.protocol_list:
          protocolList()
          sys.exit(0)

     if args.algorithm_list:
          algorithmList()
          sys.exit(0)

     if not args.fqdn:
          print '--fqdn is required.'
          parser.print_help()
          sys.exit(1)

     if not args.ssh_key:
          print '--ssh-key is required.'
          parser.print_help()
          sys.exit(1)
     else:
          ssh_key = os.path.expanduser(args.ssh_key)
          try:
               f = open(ssh_key, 'r')
          except IOError:
               print 'File "%s" does not exist.' % args.ssh_key
               sys.exit(1)
          pubkey = f.read()
          f.close()
          ssh_key = {'/root/.ssh/authorized_keys': pubkey}

     if not isValidImage(args.image):
          print 'Invalid Image: %s' % (args.image)
          sys.exit(1)

     if not isValidFlavor(args.flavor):
          print 'Invalid Flavor: %s' % (args.flavor)
          sys.exit(1)

     if not isValidProtocol(args.protocol):
          print 'Invalid Protocol: %s' % (args.protocol)
          sys.exit(1)

     if not isValidAlgorithm(args.algorithm):
          print 'Invalid Algorithm: %s' % (args.algorithm)
          sys.exit(1)

     print 'Serving your request, please wait...'
     flavor = getFlavor(args.flavor)
     image = getImage(args.image)
     sname = args.server_prefix if args.server_prefix else randomStr(8)
     lbname = args.lbname if args.lbname else  randomStr(8)
     servers = createServers(args.node_count, sname, image, flavor,
                             files=ssh_key)
     nodes = createNodes(servers, args.port_on_nodes)
     lb = createLB(lbname, args.algorithm, args.port, args.protocol, nodes)
     print "LB: %s Public: %s" % (lb.name, lb.virtual_ips[0].address)
     if not lb.get_health_monitor():
          lb.add_health_monitor('CONNECT', delay=15, timeout=60, path='/',
                                attemptsBeforeDeactivation=3)
     else:
          print "Health monitor already in place:%s" % lb.get_health_monitor()
     text = '''<html>\n<head>
    <title>The website is temporarily unavailable</title>
    <style>
      body { font-family: Tahoma, Verdana, Arial, sans-serif; }
    </style>
  </head>
  <body bgcolor="white" text="black">
    <table width="100%" height="100%">
      <tr>
        <td align="center" valign="middle">
          <h1>Ooopss! this looks like the error page on challenge10.</h1><br/>
        </td>
      </tr>
    </table>
  </body>
</html>'''
     lb.get()
     while lb.status != 'ACTIVE':
          lb.get()
          time.sleep(5)
     lb.set_error_page(text)
     container = randomStr(8)
     uploadFile(text, 'error.html', container)
     lb_ip = str(lb.virtual_ips[0].address)
     addRecord(args.fqdn, validateIPv4(lb_ip))
     print 'Connect to your LB at: http://%s' % args.fqdn
     sys.exit(0)

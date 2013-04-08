#!/usr/bin/env python

import argparse
import auth
from pyrax import utils
from pyrax import cloudfiles as cf
from pyrax import cloud_blockstorage as cbs
from pyrax import cloud_loadbalancers as clb
from pyrax import cloud_networks as cnw
import re
import sys
import time
from challenge1 import *
from challenge3 import *
from challenge4 import *
from challenge7 import *

def createSelfSignedCert(fqdn):
     ssl = {}
     cmd_key = 'openssl genrsa -out %s.key 2048' % args.fqdn
     cmd_cert = ('openssl req -new -x509 -key %(fqdn)s.key -out %(fqdn)s.cert '
                 '-days 3650 -subj /CN=%(fqdn)s') % {'fqdn': fqdn}
     os.popen(cmd_key).read()
     os.popen(cmd_cert).read()
     key_file = '%s.key' % args.fqdn
     cert_file = '%s.cert' % args.fqdn
     for ext in ['key', 'cert']:
          try:
               f = open('%s.%s' % (fqdn, ext), 'r')
          except IOError:
               print 'File "%s.%s" does not exist.' % (fqdn, ext)
               sys.exit(1)
          content = f.read()
          f.close()
          ssl[ext] = content
     return ssl

def createNetwork(name, subnet):
     found = False
     nets = cnw.list()
     for net in nets:
          if net.label == name:
               found = True
               tmp = net
     if not found:
          net = cnw.create(name, cidr=subnet)
     else:
          net = tmp
     return net

if __name__ == '__main__':
     parser = argparse.ArgumentParser(description='--- Challenge 11 ---')
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
     parser.add_argument('--network-name', metavar='NAME', default='backend',
                         help='Name to designate the network. Default: backend')
     parser.add_argument('-n', '--node-count', metavar='COUNT', default=2,
                         type=int, 
                         help='Number of Servers behind the LB, default 3')
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
     parser.add_argument('--subnet', metavar='SUBNET', default='192.168.8.0/24',
                         help=('Subnet to create in CIDR format. Default '
                               '192.168.8.0/24'))
     parser.add_argument('--vol-size', metavar='SIZE', default=100,
                         help='Size of volume 100-1024 GB. Default 100.')
     parser.add_argument('--vol-type', metavar='TYPE', default='SATA',
                         help='Type of the volume, either SATA or SSD. Default SATA.')
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

     if args.vol_type.lower() not in ['ssd', 'sata']:
          print 'Invalid volume type.'
          sys.exit(1)
     vol_type = args.vol_type.upper()
     if args.vol_size < 100 or args.vol_size > 1024:
          print 'Volume Size out of range.'
          sys.exit(1)
     vol_size = args.vol_size
     if args.subnet.count('/') != 1:
          print 'Invalid Subnet.'
          sys.exit(1)
     ip, cidr = args.subnet.split('/')
     if int(cidr) < 0 or int(cidr) > 32:
          print 'Invalid CIDR.'
          sys.exit(1)
     validateIPv4(ip)
     net = createNetwork(args.network_name, args.subnet)

     print 'Serving your request, please wait...'
     flavor = getFlavor(args.flavor)
     image = getImage(args.image)
     sname = args.server_prefix if args.server_prefix else randomStr(8)
     lbname = args.lbname if args.lbname else  randomStr(8)
     servers = createServers(args.node_count, sname, image, flavor)
     for server in servers:
          server.add_fixed_ip(args.network_name)
          server.get()
          print server.status
#     nodes = createNodes(servers, args.port_on_nodes)
#     lb = createLB(lbname, args.algorithm, args.port, args.protocol, nodes)
#     print "LB: %s Public: %s" % (lb.name, lb.virtual_ips[0].address)
#     print 'Creating cloud blockstorage and attaching to servers.'
#     for server in servers:
#          vol_name = randomStr(8)
#          vol = cbs.create(name=vol_name, size=vol_size, volume_type=vol_type)
#          utils.wait_until(server, "status", "ACTIVE", attempts=0, verbose=True)
#          vol.attach_to_instance(server, mountpoint="/dev/xvdd")
#          utils.wait_until(vol, "status", "in-use", interval=3, attempts=0, 
#                           verbose=True)
     lb = clb.list()[0]
     # LB
     lb_ssl = lb.get_ssl_termination()
     if lb_ssl:
          print "SSL termination currently in place.\n%s" % lb_ssl
     else:
          ssl = createSelfSignedCert(args.fqdn)
          lb.add_ssl_termination(securePort=443, secureTrafficOnly=False,
                                 certificate=ssl['cert'], privatekey=ssl['key'])
     lb_ip = str(lb.virtual_ips[0].address)
     addRecord(args.fqdn, validateIPv4(lb_ip))
     print 'Connect to your LB at: https://%s' % args.fqdn
     sys.exit(0)

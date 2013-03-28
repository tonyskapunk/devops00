#!/usr/bin/env python

import argparse
import os
import pyrax
import re
import sys
import time

def imageList():
     print "Available Images:"
     for img in cs.images.list():
          print img.name.lower()

def flavorList():
     print "Available Flavors:"
     for flv in cs.flavors.list():
          print flv.ram

def protocolList():
     print "Available Protocols:"
     for prot in clb.protocols:
          print prot.lower()

def algorithmList():
     print "Available Algorithms:"
     for algo in clb.algorithms:
          print algo.lower()

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

def isValidAlgorithm(algorithm):
     for algo in clb.algorithms:
         if algo.lower() == algorithm.lower():
              return True
     return False

def isValidProtocol(protocol):
     for prot in clb.protocols:
          if prot.lower() == protocol.lower():
               return True
     return False

def createLB(lbname, port, proto, nodes):
     vip = createVIP()
     lb = clb.create(lbname, port=port, protocol=proto.upper(), nodes=nodes, virtual_ips=[vip])
     return lb

def createNodes(srvs, port):
     nodes = []
     for srv in srvs:
          private = srv.networks['private']
          if ":" in private[0]:
               priv4 = private[1]
          else:
               priv4 = private[0]
          try:
               node = clb.Node(address=priv4, port=port, condition="ENABLED")
          except pyrax.exceptions.InvalidNodeCondition:
               print "Node creation failed for server: %s" % srv.name
               pass
          nodes.append(node)
     return nodes

def deleteNodes(nodes):
     for node in nodes:
          print node
     
def createVIP():
     return clb.VirtualIP(type="PUBLIC")

def randomStr(length):
    return re.sub('\W','',os.urandom(200))[:length]

def createServers(count, name, image, flavor):
     servers = []
     srvs = []
     for index in range(count):
          tmp_srv = cs.servers.create("%s%s" % (name, index), image, flavor)
          servers.append(tmp_srv)
#          srvs.append(servers[-1].id)
     print "Building Servers. Might take about  %s secs..." % (20*count)
     time.sleep(20*count)
     while True:
          if not servers:
               break
          s = servers[0]
          del servers[0]
          s.get()
          if s.networks:
               public = s.networks['public']
               if ":" in public[0]:
                    publicv4 = public[1]
               else:
                    publicv4 = public[0]
               print "%s: %s / %s" % (s.name, publicv4, s.adminPass)
               srvs.append(s)
          else:
               servers.append(s)
          time.sleep(2)
     return srvs

creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers
clb = pyrax.cloud_loadbalancers

parser = argparse.ArgumentParser(description='Cloud LBs Creator.')
parser.add_argument('-a', '--algorithm', metavar='ALGORITHM', 
                    default='round_robin',
                    help='Algorithm to use in the LB. Default round_robin')
parser.add_argument('-A', '--algorithm-list', action='store_true',
                    help='Prints the supported algorithms.')
parser.add_argument('-F', '--flavor-list', action='store_true',
                    help='Prints the available Server Flavors/Sizes.')
parser.add_argument('-f', '--flavor', metavar='SIZE', default=512, type=int,
                    help='Size to use on servers. Default 512.')
parser.add_argument('-I', '--image-list', action='store_true',
                    help='Prints the available Server Images.')
parser.add_argument('-i', '--image', metavar='IMG_NAME', default='arch',
                    help='Image to use, uses the first match. Default arch.')
parser.add_argument('-n', '--node-count', metavar='COUNT', default=2, type=int,
                    help='Number of Servers behind the LB')
parser.add_argument('-p', '--port', metavar='PORT', default=80, type=int,
                    help='Port to use in the LB. Default 80')
parser.add_argument('--protocol', metavar='PROTOCOL', default='http',
                    help='Protocol to use in the LB. Default http')
parser.add_argument('--protocol-list', action='store_true',
                    help='Prints the supported protocols.')
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

if not isValidImage(args.image):
     print "Invalid Image: %s" % (args.image)
     sys.exit(1)

if not isValidFlavor(args.flavor):
     print "Invalid Flavor: %s" % (args.flavor)
     sys.exit(1)

if not isValidProtocol(args.protocol):
     print "Invalid Protocol: %s" % (args.protocol)
     sys.exit(1)

if not isValidAlgorithm(args.algorithm):
     print "Invalid Algorithm: %s" % (args.algorithm)
     sys.exit(1)

# Name of the cloud servers
name = 'x' + randomStr(8)
flavor = [flv for flv in cs.flavors.list() if flv.ram == args.flavor][0]
image = [img for img in cs.images.list() if args.image in img.name.lower()][0]

# TODO: lbname, internal/external port, algorithm
servers = createServers(args.node_count, name, image, flavor)
nodes = createNodes(servers, 80)
lb = createLB("foo", args.port, args.protocol, nodes)
print "LB: %s Public: %s" % (lb.name, lb.virtual_ips[0].address)
sys.exit(0)

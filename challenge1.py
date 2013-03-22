#!/usr/bin/env python

import os
import pyrax
import time

count = 3
delay = 2
distro = "arch"
name = "xweb"
servers = []
size = 512

creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cs = pyrax.cloudservers

imgs = cs.images.list()
flvs = cs.flavors.list()

image = [img for img in imgs if distro in img.name.lower()][0]
flavor = [flv for flv in flvs if flv.ram == size][0]

print "Requesting  %s servers with prename: %s" % (count, name)
for index in range(count):
     servers.append(cs.servers.create("%s%s" % (name, index), image, flavor))
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
    else:
        servers.append(s)
    time.sleep(delay)

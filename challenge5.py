#!/usr/bin/env python

import argparse
import os
import pyrax
import re
import sys
import time

def createInstance(name, flavor, size):
    ins = cdb.create(name, flavor=flavor, volume=size)
    print "Name:", ins.name
    print "ID:", ins.id
    print "Status:", ins.status

def listFlavors():
    print "Available Flavors:"
    for flv in cdb.list_flavors():
        print "%s" % (flv.ram)
    sys.exit(0)

def randomStr(length):
    return re.sub('\W','',os.urandom(200))[:length]

creds_file = os.path.expanduser("~/.rackspace_cloud_credentials")
pyrax.set_credential_file(creds_file)
cdb = pyrax.cloud_databases

parser = argparse.ArgumentParser(description='Cloud DB Creator.')
parser.add_argument('-d', '--database', metavar='DBNAME', required=False,
                    help='Name to use for the DB.')
parser.add_argument('-f', '--flavor', metavar='FLAVOR',required=False,
                    help='DB Flavor, default 512.',default=512, type=int)
parser.add_argument('-i', '--instance', metavar='INST_NAME', required=False,
                    help='Name to use for the instance.')
parser.add_argument('-s', '--size', metavar='SIZE', default=1, type=int,
                    help='Size in GB of the instance [1-50].')
parser.add_argument('-u', '--username', metavar='USERNAME',  required=False,
                    help='USERNAME to use for the DB.')
parser.add_argument('-l', '--list-flavors', action='store_true', default=False,
                    help='Prints the available flavors of Cloud DBs.',
                    required=False)
args = parser.parse_args()

if args.list_flavors:
    listFlavors()

if args.size < 1 or args.size > 50:
    print "Size out of range."
    sys.exit(1)

dbname = randomStr(8) if not args.database else args.database
instance = randomStr(8) if not args.instance else args.instance
username = randomStr(8) if not args.username else args.username
password = randomStr(12)

flvs = cdb.list_flavors()
flavors = []
for flv in flvs:
    flavors.append(flv.ram)
if args.flavor not in flavors:
    print "%s is an Invalid Flavor!" % args.flavor
    listFlavors()
flavor = [flv for flv in flvs if flv.ram == args.flavor][0]

# instance creation
# TODO: validate the instance is not already created?
ins = cdb.create(instance, flavor=flavor, volume=args.size)
print "Building instance. This takes about 2 min."
time.sleep(90)

# db creation on the instance
# TODO: validate the db is not already created
while True:
    # TODO: find a way to get the instance by id
    my_ins = [tmp_ins for tmp_ins in cdb.list() if tmp_ins.id == ins.id][0]
    if my_ins.status == 'ACTIVE':
        print "Name: %s Hostname: %s Status: %s" % (my_ins.name, 
                                                    my_ins.hostname,
                                                    my_ins.status)
        break
    elif my_ins.status == 'ERROR':
        print "There was an error when building the Instance, please try again."
        sys.exit(1)
    time.sleep (5)

db = ins.create_database(dbname)
print "DBName: %s" % dbname

# user creation on the db
# TODO: validate the user is not already created
user = ins.create_user(username, password, database_names=[dbname])
print "User: %s Password: %s" % (username, password)

sys.exit(0)
# listing DBs in the instance
###dbs = inst.list_databases()
###for db in dbs:
###    print db.name

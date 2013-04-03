#!/usr/bin/env python

import argparse
import auth
import os
import sys
import time
from challenge1 import randomStr
from pyrax import cloud_databases as cdb

def listDBFlavors():
    print "Available Flavors:"
    for flv in cdb.list_flavors():
        print "%s" % (flv.ram)
    sys.exit(0)

def isDBinInstance(ins, dbname):
    if ins.list_databases():
        for db in ins.list_databases():
            if db.name == dbname:
                return True
    return False

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Cloud DB Creator.')
    parser.add_argument('-d', '--database', metavar='DBNAME', required=False,
                        help='Name to use for the DB.')
    parser.add_argument('-f', '--flavor', metavar='FLAVOR',required=False,
                        help='DB Flavor, default 512.',default=512, type=int)
    parser.add_argument('-i', '--instancename', metavar='INSTNAME', 
                        required=False, help='Name to use for the instance.')
    parser.add_argument('-s', '--size', metavar='SIZE', default=1, type=int,
                        help='Size in GB of the instance [1-50].')
    parser.add_argument('-u', '--username', metavar='USERNAME',  required=False,
                        help='USERNAME to use for the DB.')
    parser.add_argument('-l', '--list-flavors', action='store_true', 
                        default=False,required=False, 
                        help='Prints the available flavors of Cloud DBs.')
    args = parser.parse_args()

    if args.list_flavors:
        listDBFlavors()

    if args.size < 1 or args.size > 150:
        print "Size out of range."
        sys.exit(1)

    dbname = randomStr(8) if not args.database else args.database
    instancename = randomStr(8) if not args.instancename else args.instancename
    username = randomStr(8) if not args.username else args.username
    password = randomStr(12)

    flvs = cdb.list_flavors()
    flavors = []
    for flv in flvs:
        flavors.append(flv.ram)
    if args.flavor not in flavors:
        print "%s is an Invalid Flavor!" % args.flavor
        listDBFlavors()
    flavor = [flv for flv in flvs if flv.ram == args.flavor][0]

    # Instance creation
    ins = None
    if [ins for ins in cdb.list() if ins.name == instancename]:
        print "Instance already created."
    else:
        ins = cdb.create(instancename, flavor=flavor, volume=args.size)
        print "Building instance. This takes about 2 min."
        time.sleep(90)
    while True:
        # TODO: find a way to get the instance by id!
        my_ins = [tmp_ins for tmp_ins in cdb.list() if tmp_ins.id == ins.id][0]
        if my_ins.status == 'ACTIVE':
            break
        elif my_ins.status == 'ERROR':
            print "Oops an error occur!, please try again."
            my_ins.delete()
            sys.exit(1)
        time.sleep (5)

    # DB creation on the instance.
    if not isDBinInstance(ins, dbname):
        db = ins.create_database(dbname)
    # user creation on the instance/db
    if not [user for user in ins.list_users() if user.name == username]:
        user = ins.create_user(username, password, database_names=[dbname])
    else:
        password = "<your_password>"
        print "User already in place"
    print "Connect using:\nmysql -h%s -u%s -p%s %s" % (ins.hostname, username, password, dbname)
    sys.exit(0)

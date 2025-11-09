import argparse
import re

from beacon.api import GlobalScan, DiscoveryScan, BeaconScan, QueryAction, IdentifyAction, DumpAction

def mac_addr(x):
    x = x.lower()
    if not re.match("^(?:[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", x):
        raise ValueError()
    return x

def run(args):

    parser = argparse.ArgumentParser()
    subparsers = parser.add_subparsers(help='action', dest='command', required=True)
    sub = subparsers.add_parser('global',help='Scan for BLE devices')
    sub = subparsers.add_parser('discover', help = "Scan for ThermoBeacon devices")
    sub.add_argument('-mac', type=mac_addr, default=None, required=False)
    sub = subparsers.add_parser('identify', help = "Identify a device")
    sub.add_argument('-mac', type=mac_addr, required=True)
    sub = subparsers.add_parser('dump', help = "Dump logged data")
    sub.add_argument('-mac', type=mac_addr, required=True)
    sub.add_argument('-t', type=int, default = 20, metavar='<Query duration, seconds>', required=False)
    sub.add_argument('-n', type=int,  help='Number to pull', required=True)
    sub = subparsers.add_parser('query', help = "Query device for details")
    sub.add_argument('-mac', type=mac_addr, required=True)
    sub.add_argument('-t', type=int, default = 20, metavar='<Query duration, seconds>', required=False)


    args = parser.parse_args()


    cmd = args.command
    if cmd=='global':
        scan=GlobalScan()
        scan.run()
    if cmd=='discover':
        print('Discover')
        if args.mac is None:
            print('General scan')
            scan=DiscoveryScan()
            scan.run()
        else:
            print('Device scan')
            scan=BeaconScan(args.mac)
            scan.run()
    elif cmd=='query':
        act=QueryAction(args.mac,timeout=args.t)
        act.run()
    elif cmd=='identify':
        act=IdentifyAction(args.mac,timeout=args.t)
        act.run()
    elif cmd=='dump':
        act = DumpAction(args.mac, timeout=args.t,count=args.n)
        act.run()
    else:
        print('Not yet implemented')

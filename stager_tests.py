#!/usr/bin/python3

from payloads import Generator
from server import ControlTower

import os
import pwd
import time
import random
import subprocess
import threading


print('---------Stager communication test---------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

payload = \
b'\xeb\x17\x59\x31\xc0\xb0\x04\x31\xdb\xb3\x01\x31\xd2\xb2\x0d\xcd\x80\x31\xc0\xb0\x01\x31\xdb\xcd\x80\xe8\xe4\xff\xff\xff\x48\x65\x6c\x6c\x6f\x20\x57\x6f\x72\x6c\x64\x0a'

ct = ControlTower(ip, port, payload)

ct.start()

compiled_path = 'tmp/cmaster' # fixme

_ = Generator.bin_master(ip, port) # just compile

input()
quit()
proc = subprocess.Popen(['./tmp/cmaster'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate()

# sometime in the future the payload will not print anything to stdout..

print(out)
print(err)
assert b'\x01' in out # nop is the default payload
assert len(err) == 0

print('PASSED✓')

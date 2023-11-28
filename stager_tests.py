#!/usr/bin/python

from payloads import Generator
from server import ControlTower

import os
import pwd
import time
import random
import subprocess
import threading


ip = "127.0.0.1"
port = random.randint(12000, 20000)

ct = ControlTower(ip, port)

ct.start()

compiled_path = 'tmp/cmaster' # fixme

_ = Generator.bin_master(ip, port) # just compile

proc = subprocess.Popen(['./tmp/cmaster'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
out, err = proc.communicate()

print('OUT', out)
print('ERR', err)

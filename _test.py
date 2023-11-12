#!/usr/bin/python

# local tests

from payloads import Parser

url = 'http://127.0.0.1:3111/home'

parser = Parser(url)

print(parser.get_forms())
print(parser.get_inputs())
print(parser.get_js_endpoints())
print(parser.get_js_urls())


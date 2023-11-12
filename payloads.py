import re
from bs4 import BeautifulSoup
import requests

class Parser:
    forms = []
    url = ''
    js_endpoints = []

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
        js_code = ""
        for script in scripts:
            if script.string:
                js_code += script.string

        # extract urls from js
        pattern = r"(fetch|axios|\.ajax|\.get|\.post|XMLHttpRequest)\(['\"](.*?)['\"]"
        matches = re.findall(pattern, js_code)
        self.js_endpoints = [match[1] for match in matches]

    def get_inputs(self):
        return self.inputs

    def get_forms(self):
        return self.forms
    
    def get_js_endpoints(self):
        return self.js_endpoints
    
    def get_js_urls(self):
        return [(self.protocol + self.host + e) for e in self.js_endpoints]

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

            response = requests.post(action_url, data=form_data)

            print(response.content)


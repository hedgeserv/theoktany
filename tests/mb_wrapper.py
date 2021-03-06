import json
import os
import subprocess
from subprocess import Popen
from time import sleep

import requests


# Note: changing these will NOT change how the mountebank process starts.
PROTOCOL = 'http'
MOUNTEBANK_HOST = PROTOCOL + '://localhost'
MOUNTEBANK_URL = MOUNTEBANK_HOST + ':2525'
IMPOSTERS_URL = MOUNTEBANK_URL + '/imposters'


class MountebankProcess(object):
    """Wrapper for Mountebank"""
    def __init__(self):
        self.mb_proc = None
        self.imposters = []

    @property
    def url(self):
        return MOUNTEBANK_URL

    @staticmethod
    def get_imposter_url(port):
        return '{}:{}'.format(MOUNTEBANK_HOST, port)

    def start(self):
        self.mb_proc = Popen(
            'mb start', shell=True, stdin=None, stdout=subprocess.PIPE, stderr=subprocess.PIPE, close_fds=False)
        # give mb some time to spin up and open its ports
        sleep(2)
        if self.mb_proc.poll() is not None:
            raise Exception(
                'Mountebank did not start properly. Make sure that it installed and linked to your PATH. '
                'If Mountebank is running, please terminate the process and retry running the tests.')

    def is_running(self):
        return self.mb_proc.poll() is None

    def create_imposter(self, stub_filename, port=5555):
        imposter = self.create_stubs(stub_filename, port=port)
        response = requests.post(IMPOSTERS_URL, json=imposter)
        if response.status_code != 201:
            print(response.content)
            raise Exception('Could not load Mountebank imposter.')
        port = response.json()['port']
        self.imposters.append(port)

        return port

    def destroy_imposter(self, port):
        try:
            self.imposters.remove(port)
        except ValueError:
            pass
        return requests.delete("{}/imposters/:{}".format(MOUNTEBANK_HOST, port))

    @staticmethod
    def destroy_all_imposters():
        return requests.delete(IMPOSTERS_URL, verify=False)

    def stop(self):
        self.mb_proc.terminate()
        try:
            return_code = self.mb_proc.wait(timeout=5)
        except TimeoutError:
            raise Exception('Mountebank did not stop properly (it may still be running!).')

        return return_code

    @staticmethod
    def create_stubs(stub_filename, port=5555, name='imposter'):
        # shamelessly stolen from Tim and grid-webapp-client, then slightly modified somewhat modified
        absolute_path = os.path.join(os.path.dirname(__file__), stub_filename)
        with open(absolute_path, 'r') as stub_file:
            stubs = json.load(stub_file)

        # We store the body as JSON in the files for legibility but Mountebank wants the body as a string.
        for stub in stubs:
            for predicate in stub.get('predicates', []):
                if 'contains' in predicate:
                    predicate['contains']['body'] = json.dumps(predicate['contains']['body'])
            for response in stub['responses']:
                if 'is' in response:
                    if 'body' in response['is']:
                        response['is']['body'] = json.dumps(response['is']['body'])

        return {"port": port, "protocol": PROTOCOL, "name": name, "stubs": stubs}

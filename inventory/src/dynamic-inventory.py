#!/usr/bin/python3

import os
import json
import argparse

from config.settings import config
from services.AnsibleParser import AnsibleParser
from services.FormioService import Formio
from services.LoggerService import loggerService

class Inventory(object):
    def __init__(self):
        self.ansible = AnsibleParser()
        self.formio = Formio()
        self.read_cli_args()

        self.NEWCOS_SERVICE = os.getenv('NEWCOS_SERVICE')
        self.NEWCOS_SUBMISSION = os.getenv('NEWCOS_SUBMISSION')

        # Called with `--list`.
        if self.args.list:
            self.inventory = self.build_inventory()
        # Called with `--host [hostname]`.
        elif self.args.host:
            # Not implemented, since we return _meta info `--list`.
            self.inventory = self.ansible.empty_inventory()
        # If no groups or vars are present, return an empty inventory.
        else:
            self.inventory = self.ansible.empty_inventory()

        print(json.dumps(self.inventory))

    def build_inventory(self):
        if self.NEWCOS_SUBMISSION != None and len(self.NEWCOS_SUBMISSION) != 0:
            data = self.formio.get_submission(self.NEWCOS_SERVICE, self.NEWCOS_SUBMISSION)
            loggerService.info(json.dumps(data, indent=4, sort_keys=True))
        else:
            data = self.formio.get_submissions(self.NEWCOS_SERVICE)
            loggerService.info(json.dumps(data, indent=4, sort_keys=True))
        
        self.ansible.submission_adapter(data)
        return self.ansible.get_inventory()

    # Read the command line args passed to the script.
    def read_cli_args(self):
        parser = argparse.ArgumentParser()
        parser.add_argument('--list', action = 'store_true')
        parser.add_argument('--host', action = 'store')
        self.args = parser.parse_args()

if __name__ == '__main__':
    # loggerService.info('SERVICE: ' + str(NEWCOS_SERVICE))
    # loggerService.info('SUBMISSION: ' + str(NEWCOS_SUBMISSION))
    # formio = Formio()
    # inventory = AnsibleParser()
    # inventory.submission_adapter(data)
    # loggerService.info(inventory.get_inventory())
    Inventory()
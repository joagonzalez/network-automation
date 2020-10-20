import json

class AnsibleParser():
    def __init__(self, submissions=None):
        self.inventory = {
                            '_meta': {
                                'hostvars': {}
                            }
                        }

    def __str__(self):
        pass

    def submission_adapter(self, submissions):
        if len(submissions) != 0:
            for submission in submissions:
                data = submission['data']
                host = data['hostname']
                role = data['role']
                if not role in self.inventory:
                    self.inventory[role] = {}
                    self.inventory[role]['hosts'] = []
                    self.inventory[role]['vars'] = {}
                    self.inventory[role]['hosts'].append(host)
                else:
                    self.inventory[role]['hosts'].append(host)

                self.inventory['_meta']['hostvars'].update({host:data})
        else:
            self.inventory = self.empty_inventory()

    def get_inventory(self):
        return self.inventory

    # Empty inventory for testing.
    def empty_inventory(self):
        return {'_meta': {'hostvars': {}}}


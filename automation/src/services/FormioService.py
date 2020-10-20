import sys
import json
import requests
sys.path.append('../')
from config.settings import config
from services.LoggerService import loggerService
#from services.MSTeamsService import send_teams_message

# disable warning fot not verified ssl
requests.packages.urllib3.disable_warnings()

"""
PENDING: Token expiration
"""
class Formio():
    server = config['FORMIO']['URL']
    username = config['FORMIO']['USERNAME']
    password = config['FORMIO']['PASSWORD']
    token = None
    resources = {}

    def __init__(self):
        self.token = self.get_token()

    def get_token(self):
        login_info = {
            'data': {
                'email': self.username,
                'password': self.password
            }
        }

        if self.token == None:
            try:
                response = requests.post(self.server+'/user/login', json=login_info, verify=False)
                if 'x-jwt-token' in response.headers and response.headers['x-jwt-token'] != '':
                    return response.headers['x-jwt-token']
            except Exception as e:
                loggerService.error('Error getting token')
            return None

    def check_token(self):
        return self.token != None

    def get_headers(self):
        headers = {
            'Content-Type': 'application/json',
            'x-jwt-token': self.token
        }
        return headers

    def create_submission(self, resource, data):
        """
        Create a new submission into a specific resource
        """
        if self.check_token():
            headers = self.get_headers()
            
            try:
                response = requests.post(self.server+'/'+resource+'/submission',json=data, headers=headers, verify=False)        
            
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 206:
                    submission = [response.json()]
                else:
                    return response.status_code
                return response.status_code # last status code
            except Exception as e:
                loggerService.error('Error trying to get submission: ' + str(e))
                submission = str(e)
        else:
            return None

    def create_submissions(self, resource):
        """
        Create one submission for each resource within resources list in the current object
        """
        if self.check_token():
            submissions = []
            results = []
            
            headers = self.get_headers()

            for submission in self.resources[resource]:
                submissions.append({'data': submission['data']})

            for submission in submissions:
                response = requests.post(self.server+'/'+resource+'/submission',json=submission, headers=headers, verify=False)
                results.append(response.status_code)

            return response.status_code # last status code
        else:
            return None

    def get_submission(self, resource, submission_id):
        submission = None
        headers = self.get_headers()
        if self.check_token():
            try:
                response = requests.get(self.server+'/'+resource+'/submission/' + submission_id, headers=headers, verify=False)
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 206:
                    submission = [response.json()]
                else:
                    return response.status_code
            except Exception as e:
                loggerService.error('Error trying to get submission: ' + str(e))
                submission = str(e)
        return submission           

    def get_submission_filter(self, resource, field, filter):
        submissions = None
        headers = self.get_headers()
        if self.check_token():
            response = requests.get(self.server+'/'+resource+'/submission?data.'+str(field)+'='+str(filter)+'&limit=100', headers=headers, verify=False)
            if response.status_code == 200 or response.status_code == 201 or response.status_code == 206:
                submissions = response.json()
        return submissions

    def get_submissions(self, resource):
        """
        Get all submissions from a specific resource
        """
        submissions = None
        headers = self.get_headers()

        if self.check_token():
            # ?limit=999 can be added at the end of /submission
            try:
                response = requests.get(self.server+'/'+resource+'/submission?limit=5000', headers=headers, verify=False)
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 206:
                    submissions = response.json()
                    self.resources.update({resource: submissions})
                    return self.resources[resource]
                else:
                    return response.status_code
            except Exception as e:
                loggerService.error('Error trying to get submissions from: ' + str(resource))
                loggerService.error('Error description: ' + str(e))

        
    def delete_submission(self, resource, identity):
        pass
    
    def delete_submissions(self, resource):
        """
        Delete all submissions of a specific resource
        """
        results = []
        if self.get_submissions(resource):
            submissions = self.resources[resource]
            headers = self.get_headers()

            results = []
            if self.check_token():
                for submission in submissions:
                    response = requests.delete(self.server+'/'+resource+'/submission/' + submission['_id'], headers=headers, verify=False)
                    results.append(response.status_code)
        return results

    def update_submission(self, resource, submission_id, submission_data):
        submission = None
        headers = self.get_headers()
        if self.check_token():
            try:
                response = requests.put(self.server+'/'+resource+'/submission/' + submission_id, headers=headers, json=submission_data,verify=False)
                if response.status_code == 200 or response.status_code == 201 or response.status_code == 206:
                    submission = [response.json()]
                else:
                    return response.status_code
            except Exception as e:
                loggerService.error('Error trying to get submission: ' + str(e))
                submission = str(e)
        return submission 

    def open_file(self, filename, with_bom):
        data = None
        try:
            if not with_bom:
                f = open(filename)
                data = json.load(f)
            else:
                if sys.version_info.major < 3:
                    f = open(filename)
                    data = f.read().decode('utf-8-sig') # Python 2
                    return json.loads(data)
                else:
                    f = open(filename, encoding='utf-8-sig') # Python 3
                    data = json.load(f)
        except Exception as e:
            loggerService.error("Error opening requested file! \n" + str(e))
        return data

if __name__ == "__main__":
    loggerService.info('Formio interface!')
    formio = Formio()
    loggerService.info('Token: ' + str(formio.token))
    formio.get_submissions('automationSipTrunk')
    result = json.dumps(formio.resources['automationSipTrunk'][0]['data'], indent=4, sort_keys=True)
    loggerService.info(result)
    #loggerService.info(send_teams_message(result))
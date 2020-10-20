# -*- coding: utf-8 -*-
#
#  __   __.  _______ ____    __    ____   ______   ______        _______.
# |  \ |  | |   ____|\   \  /  \  /   /  /      | /  __  \      /       |
# |   \|  | |  |__    \   \/    \/   /  |  ,----'|  |  |  |    |   (----`
# |  . `  | |   __|    \            /   |  |     |  |  |  |     \   \    
# |  |\   | |  |____    \    /\    /    |  `----.|  `--'  | .----)   |   
# |__| \__| |_______|    \__/  \__/      \______| \______/  |_______/      

#   http://www.apache.org/licenses/LICENSE-2.0

########################################################################################################################
###########################################                       ######################################################
###########################################  READ ONLY LIBRARIES  ######################################################
###########################################                       ######################################################
########################################################################################################################

from builtins import range
from datetime import timedelta, datetime
import pymsteams
import requests
import random
import json
import logging
log = logging.getLogger(__name__)
import base64

import airflow
from airflow.models import DAG
from airflow.operators.bash_operator import BashOperator
from airflow.operators.dummy_operator import DummyOperator
from airflow.operators.python_operator import PythonOperator
from airflow.operators.python_operator import BranchPythonOperator

########################################################################################################################
#######################################                                  ###############################################
#######################################  CUSTOM LIBRARIES AND VARIABLES  ###############################################
#######################################                                  ###############################################
########################################################################################################################

DAGS = '/usr/local/airflow/dags'
PLAYBOOKS = '/usr/local/airflow/playbooks'
SCRIPTS = '/usr/local/airflow/scripts'
ANSIBLE_PLAYBOOK = 'sbc_audiocodes_telnet.yaml'
DAG_WORKING_FOLDER = '/usr/local/airflow/logs/newcos_dag'
BACKUP_WORKING_FOLDER = '/shared/newcos-automation/dev/logs/newcos_dag'
LOG_SERVICE = 'automationlogs'

import sys
sys.path.append(SCRIPTS + '/newcos-inventory/src')
from services.FormioService import Formio
from  services.MSTeamsService import send_teams_message

########################################################################################################################
##############################################                  ########################################################
##############################################  DAG DEFINITION  ########################################################
##############################################                  ########################################################
########################################################################################################################

args = {
    'owner': 'Airflow',
    'start_date': airflow.utils.dates.days_ago(2),
    'provide_context': True
}

dag = DAG(
    dag_id='newcos_dag',
    default_args=args,
    schedule_interval='0 0 * * *',
    dagrun_timeout=timedelta(minutes=60),
)

########################################################################################################################
##############################################                  ########################################################
##############################################  Custom Functions  ########################################################
##############################################                  ########################################################
########################################################################################################################

def teams_message(**context):
    conf = context["dag_run"].conf
    NEWCOS_SERVICE = conf['NEWCOS_SERVICE']
    NEWCOS_SUBMISSION = conf['NEWCOS_SUBMISSION']

    formio = Formio()
    
    data = formio.get_submission(NEWCOS_SERVICE, NEWCOS_SUBMISSION)
    task_id = data[0]['data']['task_id']
    submission = data[0]
    backup_date = backup_date = datetime.now().strftime("%Y-%m-%d")

    msg = 'NEWCOS_SERVICE: ' + str(NEWCOS_SERVICE) + '\n   NEWCOS_SUBMISSION: ' + NEWCOS_SUBMISSION
    f = open(DAG_WORKING_FOLDER + '/' + 'backup_' + str(task_id) + '_'+ str(backup_date) + '.conf')
    data = f.read()
    # msg += '\n   ' + str(data)

    try:
        send_teams_message(msg)
    except Exception as e:
        print('Error sending message: ' + str(e))

def context_data(**context):
    """
    Print the payload "message" passed to the DagRun conf attribute.
    :param context: The execution context
    :type context: dict
    """
    print("Remotely received value of {}".format(str(context["dag_run"].conf)))

def save_backup(**context):
    # get task env
    conf = context["dag_run"].conf
    NEWCOS_SERVICE = conf['NEWCOS_SERVICE']
    NEWCOS_SUBMISSION = conf['NEWCOS_SUBMISSION']

    print('CONF PARAMETERS FROM API: ' + str(conf))

    # get data from form.io
    formio = Formio()
    # os.environ["NEWCOS_SERVICE"] = NEWCOS_SERVICE
    # os.environ["NEWCOS_SUBMISSION"] = NEWCOS_SUBMISSION

    data = formio.get_submission(NEWCOS_SERVICE, NEWCOS_SUBMISSION)
    print(data[0]['data'])
    task_id = data[0]['data']['task_id']
    submission = data[0]
    backup_date = backup_date = datetime.now().strftime("%Y-%m-%d")
    backup_date_formio = datetime.now().strftime("%Y-%m-%d %H:%M")
    print('Hora de ultimo backup: ' + str(backup_date_formio))

    # read backup
    f = open(DAG_WORKING_FOLDER + '/' + 'backup_' + str(task_id) + '_'+ str(backup_date) + '.conf')
    data = f.read()
    print(data)

    # update submission
    print('update submission')
    submission['data']['backup'] = data
    submission['data']['last_backup'] = backup_date_formio
    formio.update_submission(NEWCOS_SERVICE, NEWCOS_SUBMISSION, submission)

    # crea logs
    print('create logs for this task')
    msg = "Backup succesfuly done!"
    submission_logs =  {
                            "data": {
                                "resource": NEWCOS_SERVICE,
                                "taskId": NEWCOS_SUBMISSION,
                                "log": msg,
                                "date": backup_date_formio
                            }
                        }

    result = formio.create_submission(LOG_SERVICE, submission_logs)
    print(result)
    
def send_email(**context):
    # get task env
    conf = context["dag_run"].conf
    NEWCOS_SERVICE = conf['NEWCOS_SERVICE']
    NEWCOS_SUBMISSION = conf['NEWCOS_SUBMISSION']

    # get data from form.io
    formio = Formio()
    data = formio.get_submission(NEWCOS_SERVICE, NEWCOS_SUBMISSION)

    task_id = data[0]['data']['task_id']
    submission = data[0]
    backup_date = backup_date = datetime.now().strftime("%Y-%m-%d")
    server = "http://newcos-sandbox-01.smq.net:3002/api/v1/events"

    msg = 'NEWCOS WORKFLOW RUN: NEWCOS_SERVICE: ' + str(NEWCOS_SERVICE) + '\n   NEWCOS_SUBMISSION: ' + NEWCOS_SUBMISSION

    # mail body
    body = {
        "event":"sendMail",
        "tenant_id":"58005ddb-3d82-4718-9e75-ec5c71cca7ec",
        "transaction_id":"5ee9038471ca5d0f6fd02175",
        "transaction_src":"newcos-manager@latest",
        "transaction_reply" : "event-reply",
        "user_graph":"teams.admin@newtech.com.ar",
        "pass_graph":"Password01",
        "subject": 'WORKFLOW newcos_dag | TASK ID: ' + str(task_id) + ' | DATE: ' + str(backup_date),
        "to": ["dev@newtech.com.ar", "joaquin.gonzalez@newtech.com.ar"],
        "contentType" : "text",
        "bodyText" : msg,
        "attachment" : True,
        "file" : BACKUP_WORKING_FOLDER + '/' + 'backup_' + str(task_id) + '_'+ str(backup_date) + '.conf'
    }

    # send mail
    try:
        response = requests.post(server,json=body)
    except Exception as e:
        print('Error sending email: ' + str(e))

########################################################################################################################
###############################################                     ####################################################
###############################################  TASKS DEFINITIONS  ####################################################
###############################################                     ####################################################
########################################################################################################################
environment_ansible = {
                        'NEWCOS_SERVICE': '{{ dag_run.conf["NEWCOS_SERVICE"] if dag_run else "" }}',
                        'NEWCOS_SUBMISSION': '{{ dag_run.conf["NEWCOS_SUBMISSION"] if dag_run else "" }}',
                        'DAG_WORKING_FOLDER': DAG_WORKING_FOLDER    
                      }

templated_command =  'cd ' + PLAYBOOKS + \
        ' && ansible-playbook -i ' + SCRIPTS + '/newcos-inventory/src/newcos-inventory.py ' + PLAYBOOKS + \
        '/' + ANSIBLE_PLAYBOOK + ' && printenv'

newcos_init = BashOperator(task_id='newcos_init',bash_command='ansible --version -vvv', dag=dag,)
teams_message = PythonOperator(task_id='teams_message', python_callable=teams_message,dag=dag,)
newcos_end = BashOperator(task_id='newcos_end', bash_command='echo "run_id={{ run_id }} | dag_run={{ dag_run }}"', dag=dag,)
ansible_playbook_sbc = BashOperator(task_id='playbook_sbc',bash_command=templated_command, env=environment_ansible, dag=dag,)
context_data = PythonOperator(task_id='dag_context', python_callable=context_data, dag=dag)
save_backup = PythonOperator(task_id='save_backup', python_callable=save_backup, dag=dag)
send_email = PythonOperator(task_id='send_email', python_callable=send_email, dag=dag)

########################################################################################################################
################################################                  ######################################################
################################################  TASKS WORKFLOW  ######################################################
################################################                  ######################################################
########################################################################################################################

newcos_init >> ansible_playbook_sbc
newcos_init >> context_data
ansible_playbook_sbc >> save_backup
save_backup >> teams_message
context_data >> teams_message
teams_message >> send_email
send_email >> newcos_end

if __name__ == "__main__":
    dag.cli()

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
DAG_WORKING_FOLDER = '/usr/local/airflow/logs/network_dag'
BACKUP_WORKING_FOLDER = '/shared/network-automation/dev/logs/network_dag'
LOG_SERVICE = 'automationlogs'

import sys
sys.path.append(SCRIPTS + '/network-inventory/src')
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
    dag_id='network_dag',
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
    NETWORK_SERVICE = conf['NETWORK_SERVICE']
    NETWORK_SUBMISSION = conf['NETWORK_SUBMISSION']

    formio = Formio()
    
    data = formio.get_submission(NETWORK_SERVICE, NETWORK_SUBMISSION)
    task_id = data[0]['data']['task_id']
    submission = data[0]
    backup_date = backup_date = datetime.now().strftime("%Y-%m-%d")

    msg = 'NETWORK_SERVICE: ' + str(NETWORK_SERVICE) + '\n   NETWORK_SUBMISSION: ' + NETWORK_SUBMISSION
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
    NETWORK_SERVICE = conf['NETWORK_SERVICE']
    NETWORK_SUBMISSION = conf['NETWORK_SUBMISSION']

    print('CONF PARAMETERS FROM API: ' + str(conf))

    # get data from form.io
    formio = Formio()
    # os.environ["NETWORK_SERVICE"] = NETWORK_SERVICE
    # os.environ["NETWORK_SUBMISSION"] = NETWORK_SUBMISSION

    data = formio.get_submission(NETWORK_SERVICE, NETWORK_SUBMISSION)
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
    formio.update_submission(NETWORK_SERVICE, NETWORK_SUBMISSION, submission)

    # crea logs
    print('create logs for this task')
    msg = "Backup succesfuly done!"
    submission_logs =  {
                            "data": {
                                "resource": NETWORK_SERVICE,
                                "taskId": NETWORK_SUBMISSION,
                                "log": msg,
                                "date": backup_date_formio
                            }
                        }

    result = formio.create_submission(LOG_SERVICE, submission_logs)
    print(result)
    
def send_email(**context):
    # get task env
    conf = context["dag_run"].conf
    NETWORK_SERVICE = conf['NETWORK_SERVICE']
    NETWORK_SUBMISSION = conf['NETWORK_SUBMISSION']

    # get data from form.io
    formio = Formio()
    data = formio.get_submission(NETWORK_SERVICE, NETWORK_SUBMISSION)

    task_id = data[0]['data']['task_id']
    submission = data[0]
    backup_date = backup_date = datetime.now().strftime("%Y-%m-%d")
    server = "http://sandbox-01:3002/api/v1/events"

    msg = 'NETWORK WORKFLOW RUN: NETWORK_SERVICE: ' + str(NETWORK_SERVICE) + '\n   NETWORK_SUBMISSION: ' + NETWORK_SUBMISSION

    # mail body
    body = {
        "event":"sendMail",
        "tenant_id":"58005ddb-3d82-4718-9e75-ec5c71cca7ec",
        "transaction_id":"5ee9038471ca5d0f6fd02175",
        "transaction_src":"test@latest",
        "transaction_reply" : "event-reply",
        "user_graph":"user",
        "pass_graph":"password",
        "subject": 'WORKFLOW network_dag | TASK ID: ' + str(task_id) + ' | DATE: ' + str(backup_date),
        "to": ["mail1", "mail2"],
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
                        'NETWORK_SERVICE': '{{ dag_run.conf["NETWORK_SERVICE"] if dag_run else "" }}',
                        'NETWORK_SUBMISSION': '{{ dag_run.conf["NETWORK_SUBMISSION"] if dag_run else "" }}',
                        'DAG_WORKING_FOLDER': DAG_WORKING_FOLDER    
                      }

templated_command =  'cd ' + PLAYBOOKS + \
        ' && ansible-playbook -i ' + SCRIPTS + '/dynamic-inventory/src/dynamic-inventory.py ' + PLAYBOOKS + \
        '/' + ANSIBLE_PLAYBOOK + ' && printenv'

network_init = BashOperator(task_id='network_init',bash_command='ansible --version -vvv', dag=dag,)
teams_message = PythonOperator(task_id='teams_message', python_callable=teams_message,dag=dag,)
network_end = BashOperator(task_id='network_end', bash_command='echo "run_id={{ run_id }} | dag_run={{ dag_run }}"', dag=dag,)
ansible_playbook_sbc = BashOperator(task_id='playbook_sbc',bash_command=templated_command, env=environment_ansible, dag=dag,)
context_data = PythonOperator(task_id='dag_context', python_callable=context_data, dag=dag)
save_backup = PythonOperator(task_id='save_backup', python_callable=save_backup, dag=dag)
send_email = PythonOperator(task_id='send_email', python_callable=send_email, dag=dag)

########################################################################################################################
################################################                  ######################################################
################################################  TASKS WORKFLOW  ######################################################
################################################                  ######################################################
########################################################################################################################

network_init >> ansible_playbook_sbc
network_init >> context_data
ansible_playbook_sbc >> save_backup
save_backup >> teams_message
context_data >> teams_message
teams_message >> send_email
send_email >> network_end

if __name__ == "__main__":
    dag.cli()

#!/usr/bin/python3

import paramiko
import pysftp
import csv

# NSO info, update ip, username password, Authotization Basic and http/https 
nso_srv = {'host':'198.18.130.26','port':'2022','username':'admin','password':'admin','hostkey_verify':False, 'http_or_s':'http', 'http_prt':'8080'}
# For ssh connection
nso_srv_ssh = {'host':nso_srv['host'], 'port':'22','username':'lsse', 'password':'C1sco123'}

# NSO File Path
file_path_nso ='/home/lsse/ncs-run/'

def get_files():
    ''' 
    Connect to the NSO via SSH, create a backup of the ptrace.csv file with the date-hour of the NSO system.
    Delete the ptrace.csv file (the NSO will create again when it writes the trace file)
    Download a copy of "ptrace_date.csv" file in the server where we are executing this script.
    Create a list of dictionaries with the CSV file
    '''
    try:
        client = paramiko.SSHClient()
        client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        client.connect(nso_srv_ssh['host'],username=nso_srv_ssh['username'], password=nso_srv_ssh['password'])
        stdin, stdout, stderr = client.exec_command('date +"%m-%d-%y-%H%M%S"')
        file_date = stdout.read().decode().strip()
        stdin, stdout, stderr = client.exec_command('cp ' + file_path_nso + 'logs/ptrace.csv ' + file_path_nso + 'logs/ptrace_' + file_date + '.csv')
        stdin, stdout, stderr = client.exec_command('cp ' + file_path_nso + 'logs/audit-network.log ' + file_path_nso + 'logs/audit-network_' + file_date + '.log')
        output_err = stderr.read().decode().strip()
        if output_err == '':
            #stdin, stdout, stderr = client.exec_command('rm /home/lsse/ncs-run/logs/ptrace.csv')
            client.close()
            client.close()
            cnopts = pysftp.CnOpts()
            cnopts.hostkeys = None   
            with pysftp.Connection(host=nso_srv_ssh['host'],port=int(nso_srv_ssh['port']),username=nso_srv_ssh['username'], password=nso_srv_ssh['password'], cnopts=cnopts) as conn:
                conn.get(file_path_nso + 'logs/ptrace_' + file_date + '.csv')
                conn.get(file_path_nso + 'logs/audit-network_' + file_date + '.log')
            
        else:
            print(output_err)
    except:
        print('failed to establish connection to targeted server')

    try:
        with open('ptrace_' + file_date + '.csv', 'r') as f:
            csv_reader = csv.DictReader(f)
            records = list(csv_reader)

    except:
        print('failed to read CSV file')


    try:
        with open('audit-network_' + file_date + '.log', 'r') as f:
            commit_config = f.readlines()

    except:
        print('failed to read audit-network file')

    return [records,commit_config]

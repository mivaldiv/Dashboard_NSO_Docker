#!/usr/bin/python3

import csv
from datetime import datetime
import json

class ptrace_object:
    '''
    Object created to get all the ptrace usefull information
    '''
    def __init__(self,transaction_id):
        self.transaction_id = transaction_id
        self.all_info = []
        self.type = None
        self.context = None
        self.timestamp = None
        self.device_list = []
        self.service_list = []
        self.device_number = None
        self.service_number = None
        self.commit = False
        self.duration = None
        self.ini_timestamp= None

    def add_info_ptrace(self,ptrace_info):
        self.all_info.append(ptrace_info)

    ''''
    In the object in All_INFO where we can find all the entries for a specific transaction_id
    we look for key words like DEVICE, SERVICE, PHASE
    '''
    def services_ptrace(self):
        flag = True
        for n in self.all_info:
            if flag:
                self.type = n['MESSAGE'].replace(" ", "_")
                self.context = n['CONTEXT']
                self.ini_timestamp = n['TIMESTAMP']
                flag = False
            
            if n['DEVICE'] != '':
                self.device_list.append(n['DEVICE'])

            if n['SERVICE'] != '':
                self.service_list.append(n['SERVICE'])

            if n['PHASE'] == 'commit':
                self.commit = True

        self.device_list = list(dict.fromkeys(self.device_list))
        self.service_list = list(dict.fromkeys(self.service_list))
        self.device_number = len(self.device_list)
        self.service_number = len(self.service_list)
        self.timestamp = n['TIMESTAMP'][:10]
        self.duration = n['DURATION']


def convert_dates():
    ''' 
    Use an old ptrace file, convert the dates to current date and continue the analysis
    '''

    try:
        with open('ptrace_log.csv', 'r') as f:
            csv_reader = csv.DictReader(f)
            records_old = list(csv_reader)

            timestamp_list = []
            timestamp_dict = {}
            records = []

            for i in records_old:
                timestamp_list.append(i['TIMESTAMP'][:10])
            
            timestamp_list = sorted(set(timestamp_list),reverse=True)

            date = datetime.now().date().strftime('%Y-%m-%d')

            for i in range(len(timestamp_list)):
                date = datetime.now().date() - timedelta(days=i)
                date = date.strftime('%Y-%m-%d')
                timestamp_dict.update({timestamp_list[i]:date})

            for i in records_old:
                i['TIMESTAMP'] = timestamp_dict[i['TIMESTAMP'][:10]] + i['TIMESTAMP'][10:]
                records.append(i)

            records_keys = records[0].keys()

            with open('ptrace_convert.csv', 'w', newline='') as output_file:
                dict_writer = csv.DictWriter(output_file, records_keys)
                dict_writer.writeheader()
                dict_writer.writerows(records)

    except:
        print('failed to read ptrace_log.cvs file')


    return records


def process_progress_info(info):
    '''
    Create object for each transaction-id.
    Each object will have timestamp, type, context, device_list, service_list.
    '''
    transaction_list = []

    '''
    In this function we get all the information for each Transaction ID
    The objects_ptrace has transaction_id and all_info where we have all the entries related with that transaction_id
    '''
    for i in info:
        transaction_list.append(i['TRANSACTION ID'])
    transaction_list = set(transaction_list)
    
    objects_ptrace = []
    cont = 0
    for m in transaction_list:
        objects_ptrace.append(ptrace_object(m))
        for i in info:
            if m == i['TRANSACTION ID']:
                objects_ptrace[cont].add_info_ptrace(i)
        cont = cont + 1

    for m in range(len(objects_ptrace)):
        objects_ptrace[m].services_ptrace()

    change_days = []

    for m in objects_ptrace:
        change_days.append(m.timestamp)
    
    change_days = list(dict.fromkeys(change_days))

    ptrace_dict = []

    for i in objects_ptrace:
        ptrace_dict.append({
            'transaction_id': i.transaction_id,
            'ini_timestamp': i.ini_timestamp,
            'day': i.timestamp,
            'all_info': i.all_info,
            'type': i.type,
            'context': i.context,
            'duration': i.duration,
            'device_list': i.device_list,
            'device_number': i.device_number,
            'service_list': i.service_list,
            'service_number': i.service_number,
            'commit': i.commit})

    result = [ptrace_dict, change_days]
    return result
    

def analyze_progress_info(info, change_days):
    '''
    Create object for each transaction-id.
    Each object will have timestamp, type, context, device_list, service_list.
    '''

    '''
    In this function we get all the information for each Transaction ID
    The objects_ptrace has transaction_id and all_info where we have all the entries related with that transaction_id
    '''

    type_dev_count = {}
    context_dev_count = {}
    type_serv_count = {}
    context_serv_count = {}
    objects_ptrace_type = {}
    objects_ptrace_context = {}
    duration_time = {}

    ptrace_type_date = {}
    ptrace_context_date = {}


    for i in change_days:
        objects_ptrace_type[i] = []
        objects_ptrace_context[i] = []
        type_dev_count[i] = {}
        type_serv_count[i] = {}
        context_dev_count[i] = {}
        context_serv_count[i] = {}
        duration_time[i] =[] 

    for m in info:
        objects_ptrace_type[m['day']].append(m['type'])
        objects_ptrace_context[m['day']].append(m['context'])
        duration_time[m['day']].append({'transaction_id':m['transaction_id'],'duration':float(m['duration']),'type':m['type'],'context':m['context'],'device_list':m['device_list'],'service_list':m['service_list']})

    for k, m in objects_ptrace_type.items():
        ptrace_type_date[k] = {i:m.count(i) for i in m}

    for k, m in objects_ptrace_context.items():
        ptrace_context_date[k] = {i:m.count(i) for i in m}


    for k, m in ptrace_type_date.items():
        for i in m.keys():
            type_dev_count[k][i] = 0
            type_serv_count[k][i] = 0

    for k, m in ptrace_context_date.items():
        for i in m.keys():
            context_dev_count[k][i] = 0
            context_serv_count[k][i] = 0

    for m in info:
        if m['commit']:
            type_dev_count[m['day']][m['type']] = type_dev_count[m['day']][m['type']] + m['device_number']
            type_serv_count[m['day']][m['type']] = type_serv_count[m['day']][m['type']] + m['service_number']
            context_dev_count[m['day']][m['context']] = context_dev_count[m['day']][m['context']] + m['device_number']
            context_serv_count[m['day']][m['context']] = context_serv_count[m['day']][m['context']] + m['service_number']




    tables_ptrace = [ptrace_type_date,ptrace_context_date,type_dev_count,context_dev_count,type_serv_count, context_serv_count, duration_time, info]

    '''
    ptrace_type_date: Dictionary, the key is the date and the info has the transaction type (sync-from, check-sync, applying_transaction, restconf_get, etc) and the number of each one
    ptrace_context_date: Dictionary, the key is the date and the info has the context information (cli, webui, rest, system, etc) and the number of each one
    type_dev_count: Dictionary, the key is the date and the info has the number of devices modified per each transaction type
    type_serv_count: Dictionary, the key is the date and the info has the number of services modified for each transaction type
    context_dev_count: Dictionary, the key is the date and the info has the number of devices modified per each context
    context_serv_count: Dictionary, the key is the date and the info has the number of services modified for each context
    duration_time: Dictionary, they key is the date and the info has "transaction_id, duration, type, context, device_list, service_list
    '''

    return tables_ptrace



def analyze_audit(info, ptrace):
    '''
    In this function we are going to process the network-audit log (username, session_id, transaction_id, device_name, full_configuration)
    This information with be written in JSON and then written in mongodb
    '''
    file_audit = []
    transactions_list = []

    for i in info:
        if '<INFO>' in i:
            detail = i.split()
            time_audit = detail[1]
            user_name = detail[6].split('/')[0]
            session_id = detail[6].split('/')[1]
            transaction_id = detail[8]
            device = detail[12]
            for n in ptrace:
                if n['transaction_id'] == transaction_id:
                    ini_timestamp = n['ini_timestamp']
        elif 'BEGIN EDIT' in i:
            config = []
        elif 'END EDIT' in i:
            # config = ''.join(config)
            if transaction_id in transactions_list:
                device_info = {
                    'Device_Name': device,
                    'Time_Config': time_audit,
                    'Config': config
                    }
                for n in file_audit:
                    if n['Transaction_ID'] == transaction_id:
                        n['Device'].append(device_info)
            else:
                audit_data = {
                    'User_Name': user_name,
                    'Session_ID': session_id,
                    'Transaction_ID': transaction_id,
                    'Init_Transaction_Time': datetime.strptime(ini_timestamp,'%Y-%m-%dT%H:%M:%S.%f'),
                    'Device': [{
                        'Device_Name': device,
                        'Time_Config': time_audit,
                        'Config': config
                    }]
                }
                file_audit.append(audit_data)
                transactions_list.append(transaction_id)
        else:
            config.append(i.replace('\n',''))

    return file_audit





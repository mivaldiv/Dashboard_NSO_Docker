#!/usr/bin/python3
import get_files
import info_analysis
import write_databases
import info_nso_queries

import csv
import re
import sys
import requests
import time
import logging
from datetime import datetime
from datetime import timedelta

import urllib3
urllib3.disable_warnings()


date = datetime.now().date().strftime('%Y-%d-%m')
console_formartter = logging.Formatter('%(asctime)s:module:%(module)s>> %(message)s')
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.INFO)
console_handler.setFormatter(console_formartter)
my_logger = logging.getLogger()
my_logger.addHandler(console_handler)


def devices_info(var_conditions):
    devices_summary_1 = info_nso_queries.device_get_and_set_priority(var_conditions)
    my_logger.warning(f"\n {'= devices_summary_1 ='*10} \n {devices_summary_1}")
    
    devices_summary_2 = info_nso_queries.devices_summary_wPriority(devices_summary_1)
    my_logger.warning(f"\n {'= devices_summary_2 / 0 ='*5} \n {devices_summary_2[0]}")
    my_logger.warning(f"\n {'= devices_summary_2 / 1 ='*5} \n {devices_summary_2[1]}")
    my_logger.warning(f"\n {'= devices_summary_2 / 2 ='*5} \n {devices_summary_2[2]}")
    
    devices_summary = info_nso_queries.devices_summary_short(devices_summary_2[1])
    my_logger.warning(f"\n {'= devices_summary ='*5} \n {devices_summary}")
    
    #print(f'{}')
    my_logger.error(f"{write_databases.write_to_influx('devices', devices_summary_2[2])}")


def services_info(var_conditions):
    service_dict = info_nso_queries.services_get_dict()
    my_logger.warning(f"\n {'= Service_Dict ='*10} \n {service_dict} \n")

    srv = info_nso_queries.services_get_summary(service_dict,var_conditions)
    my_logger.warning(f"\n {'=='*10} \n {srv[0]}")
    my_logger.warning(f"\n {'=='*10} \n {srv[1]}")

    #print(f'{write_to_influx("services", srv[1])}')
    my_logger.error(f"{write_databases.write_to_influx('services', srv[1])}")


def changes_info():
    changes_summary = info_nso_queries.get_rollbacks_info()
    my_logger.warning(f"\n\n {changes_summary} \n\n")
    #print(write_to_influx('changes', changes_summary))
    my_logger.error(f"{write_databases.write_to_influx('changes', changes_summary)}")



def licenses_info():
    licenses = info_nso_queries.licenses_get_raw()
    #print(write_to_influx('licenses', licenses))
    my_logger.error(f"{write_databases.write_to_influx('licenses', licenses)}")


def information_analysis():
    files_info = []
    ptrace_log_file = False
    if ptrace_log_file:
        files_info[0] = info_analysis.convert_dates()
    else:
        files_info = get_files.get_files()
    
    # progress_info is a list, the first element is a dictionary with ptrace information and change_days
    print("------ Start process_progress_info ------")
    progress_info = info_analysis.process_progress_info(files_info[0])
    print("------ Start write_databases.write_to_mongodb('db_raw_info', progress_info) ------")
    progress_info_db, change_days = write_databases.write_to_mongodb('db_raw_info', progress_info)
    #my_logger.error(f"{write_databases.write_to_mongodb('db_raw_info', progress_info)}")

    print("------ Start info_analysis.analyze_progress_info ------")
    progress_info = info_analysis.analyze_progress_info(progress_info_db, change_days)
    print("------ Start write_databases.write_to_influx ------")
    my_logger.error(f"{write_databases.write_to_influx('ptrace', progress_info)}")

    print("------ Start info_analysis.analyze_audit ------")
    network_audit = info_analysis.analyze_audit(files_info[1], progress_info[7])
    print("------ Start write_databases.write_to_mongodb('nso_changes', network_audit) ------")
    my_logger.error(f"{write_databases.write_to_mongodb('nso_changes', network_audit)}")


    return


def main():
    time.sleep(1)
    try:
        verbose = sys.argv[1]
    except:
        verbose = ''
    
    try:
        file_csv = sys.argv[2]
    except:
        file_csv = "service_priority.csv"

    # ERROR < WARNING < INFO
    if 'vv' in verbose:    
        vb = 'INFO'
    elif 'v' in verbose:
        vb='WARNING'
    else:
        vb ='ERROR'
    my_logger.setLevel(eval(f"logging.{vb}"))

    try:
        conditions = info_nso_queries.read_and_fix(f"service_priority.csv")
        my_logger.warning(f"\n\n CSV read completed \n\n")
        devices_info(conditions[0])
        services_info(conditions[1])
        changes_info()
        licenses_info()
        print("------ information_analysis ------")
        information_analysis()

    except Exception as e:
        #print(f"{}")
        my_logger.error(f"{str(e)}")
    finally:
        #print("------ COMPLETE ------")
        my_logger.error(f"------ COMPLETE ------")

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        pass

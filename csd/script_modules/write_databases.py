#!/usr/bin/python3
import pymongo
import re
from datetime import datetime
from influxdb_client import InfluxDBClient, Point, WritePrecision
from influxdb_client.client.write_api import SYNCHRONOUS


# You can generate a Token from the "Tokens Tab" in the UI, this is fix in this code, and docker compose for influxdb and grafana
influx_srv = {'url':'http://influxdb_css:8086','token':'P4By5dsQDzgqtZAGrGSUZrrJo22ALYM3-SkdlWYPji8aJK2DtW9o0vXP1N5cEq69TPL8mKPxr4mxxYfJdSFKNA=='}
# Influx bucket & org
influx_db_info  = ('css','cisco')

# MongoDB information
mongo_myclient = pymongo.MongoClient('mongodb://mongodb_css:27017/')
mongo_database = mongo_myclient['nso_info']


def write_to_influx(var_type, var_summary):
    # print summary before write to DB
    ''' 
    if not var_type == 'licenses':
        my_logger.warning(f"{var_type} {var_summary}")
        #print(var_type, var_summary)
        my_logger.error(f"{var_type} {var_summary}")
        for l in var_summary:
            my_logger.warning(f"{l} ")
    '''
    try:
        date_influx_timestamp = str(int(datetime.strptime(datetime.now().date().strftime('%Y-%m-%d'), '%Y-%m-%d').timestamp())) + "000000000"
        client = InfluxDBClient(**influx_srv)
        write_api = client.write_api(write_options=SYNCHRONOUS)
        if var_type == 'devices':
            for row in var_summary[1:]:
                data = f"priorities,ned={row[0]} p1={row[1]},p2={row[2]},p3={row[3]},p4={row[4]},p5={row[5]} " + date_influx_timestamp
                # my_logger.warning(f"{data}")
                write_api.write(*influx_db_info,data)
            return 'ok'
        elif var_type == 'services':
            for row in var_summary[1:]:
                data = f"services,service={row[0]} p1={row[1]},q1={row[2]},p2={row[3]},q2={row[4]},p3={row[5]},q3={row[6]},p4={row[7]},q4={row[8]},p5={row[9]},q5={row[10]} " + date_influx_timestamp
                # my_logger.warning(f"{data}")
                write_api.write(*influx_db_info,data)
            return 'ok'
        elif var_type == 'licenses':
            #If no Smart-license config, NSO-network-element show a Count summary
            if "NSO-network-element" in var_summary.keys():
                data = f"""licenses,license="NSO-network-element" count={var_summary['NSO-network-element']['Count']},status="{var_summary['NSO-network-element']['Status']}" """ + date_influx_timestamp
            else:
                count = 0 
                for entry in var_summary.values():
                    if 'Count' in entry.keys():
                        count += int(entry['Count'])
                data = f"""licenses,license="NSO-platform-production" count={count},status="{var_summary['NSO-platform-production']['Status']}" """ + date_influx_timestamp
            #print(data)
            #my_logger.error(f"{data}")
            write_api.write(*influx_db_info,data)
            return 'ok'
        elif var_type == 'ptrace':
            for k, m in var_summary[0].items():
                for row, q in m.items():
                    data = f"type_count1,Type={row} Quantity={q} " + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    #point = Point("test_count").tag("Type", row).field("Qty",q).time(int(datetime.strptime(k,'%Y-%m-%d').timestamp()),write_precision=)
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            for k, m in var_summary[1].items():
                for row, q in m.items():
                    data = f"context_count1,Context={row} Quantity={q} " + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            for k, m in var_summary[2].items():
                for row, q in m.items():
                    data = f"type_dev_count1,Type={row} Quantity={q} " + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            for k, m in var_summary[3].items():
                for row, q in m.items():
                    data = f"context_dev_count1,Context={row} Quantity={q} " + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            for k, m in var_summary[4].items():
                for row, q in m.items():
                    data = f"type_serv_count1,Type={row} Quantity={q} " + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            for k, m in var_summary[5].items():
                for row, q in m.items():
                    data = f"context_serv_count1,context={row} Quantity={q} " + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            for k, m in var_summary[6].items():
                for q in m:
                    if len(q['service_list']) != 0:
                        q['service_list'] = str(q['service_list'])
                        q['service_list'] = re.search('\/(.*)\[', q['service_list']).group(1)
                    data = f"""transaction_of_duration1,Transaction_id="{q['transaction_id']}",Type="{q['type']}",Context="{q['context']}",Device_list="{"_".join(q['device_list'])}",Service_list="{q['service_list']}" Duration={q['duration']} """ + str(int(datetime.strptime(k,'%Y-%m-%d').timestamp())) + "000000000"
                    # my_logger.warning(f"{data}")
                    write_api.write(*influx_db_info,data)
            return 'ok'
        elif var_type == 'changes':
            for srv, qty in var_summary.items():
                data = f"""changes,change={srv} qty={qty} """ + date_influx_timestamp
                #my_logger.warning(f"{data}")
                write_api.write(*influx_db_info,data)
            return 'ok'
    except Exception as e:
        return f'fail: {e}'


def write_to_mongodb(var_type, mongo_info):
    try:
        if var_type == 'nso_changes':
            mongo_collection = mongo_database['change_info']
            x = mongo_collection.insert_many(mongo_info)
            #my_logger.warning(f"{x.inserted_ids}")
        return 'ok'

    except Exception as e:
        return f'fail: {e}'



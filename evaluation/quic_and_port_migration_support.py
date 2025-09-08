import csv
import sys
import os
from datetime import datetime
from datetime import date
from threading import Thread
from multiprocessing import Pool
from multiprocessing import cpu_count
import subprocess
import pandas as pd
import socket
import pyasn
from tranco import Tranco

asndb = pyasn.pyasn('ipasn_20240227.dat')
t = Tranco(cache = True, cache_dir = '.tranco')
if len(sys.argv) > 1:
    date = sys.argv[1]
    latest_list = t.list(date)
else:
    date = str(date.today())
    latest_list = t.list()
ofname = f'tranco_{date}.csv'
otxt = f'output_port_{date}.txt'

def test_h3(row):

    line = str(row[0]) + '\t' + row[1] 
    result = [[False, False], [False, False]]

    try:
        ip = socket.gethostbyname(row[1])
        asn = asndb.lookup(ip)
    except socket.error as e:
        ip = 'Error'
        asn = 'Error'

    process = None

    def quic_get(setting):

        # Test both example.com and www.example.com
        www = ['', 'www.']

        for i in [0, 1]:
            domain = f'https://{www[i]}{row[1]}'
            nonlocal process
            process_list = ['/home/ubuntu/Default/quic_client',
                            '--disable_certificate_verification',
                            '--quiet',
                            domain]
            if setting == 'port':
                process_list.append('--num_requests=2')
            if ip != 'Error':
                process_list.append(f'--host={ip}')

            try:
                process = subprocess.Popen(
                    process_list,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
                stdout, stderr = process.communicate()
                stdout = stdout.decode('utf-8').strip()
                stderr = stderr.decode('utf-8').strip()
            except Exception as e:
                print('Error: ', e)

            if stdout:
                result[0][i] = True
                if len(stdout) >= 34:
                    if 'Request failed' in stdout[-34:-2]:
                        result[0][i] = False
                        continue
                if result[0][i] == True and stderr == '':
                    result[1][i] = True
                    break
        
    thread = Thread(target = quic_get, args=('port',))
    thread.start()
    thread.join(timeout = 500)

    if thread.is_alive():
        if process:
            process.kill()
            thread.join()

    h3 = str(result[0][0] | result[0][1])
    cm = str(result[1][0] | result[1][1])

    line = f'{line}\t{h3}\t{cm}\t{ip}\t{asn}'
    print(line, flush = True)
    append = open(otxt, 'a')
    append.write(f'{line}\n')
    append.close()

    return

if __name__ == '__main__':

    start = datetime.now()

    latest_list = {'index': range(1, 1000001), 'domain': latest_list.top(1000000)}
    df = pd.DataFrame(latest_list)
    df.to_csv(ofname, header = None, index = False)
    t = None
    latest_list = None
    df = None
    
    write = open(otxt, 'w')
    write.write('Num\tDomain\tQUIC\tConnection migration\tIP\tASN\n')
    write.close()

    with open(ofname) as csvfile:
        csv_reader = csv.reader(csvfile)

        pool = Pool(500)
        h3_domains = pool.map(test_h3, csv_reader)

    df_output = pd.read_csv(otxt, delimiter = '\t')
    df_output = df_output.sort_values(by = 'Num')

    df_output['ASN_Clean'] = df_output['ASN'].str.extract('\((\d+),*').fillna('')

    quic = df_output['QUIC'].value_counts()[True]
    cm = df_output['Connection migration'].value_counts()[True]
    print(f'QUIC support: {quic}')
    print(f'Connection migration support: {cm}')
    with open('quic_scan_results_port.csv', 'a') as f:
        writer = csv.writer(f)
        writer.writerow([date, quic, cm])

    df_output.to_csv(f'output_union_port_{date}.csv', index = False)

    end = datetime.now()
    print(end - start)

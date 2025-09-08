from json import load
from selenium import webdriver
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import numpy as np
import matplotlib.pyplot as plt
import subprocess
import time
import sys

if len(sys.argv) < 3:
    exit
else:
    NUM_REQUESTS = int(sys.argv[1])
    domain = sys.argv[2]

# get latency (ms) for requesting the desired server file
def get_latency_ms(domain):
    opt = Options()
    opt.add_argument('--headless')
    opt.add_argument('--no-sandbox')
    opt.add_argument('--disable-dev-shm-usage')
    opt.add_argument('--enable-quic')
    opt.add_argument('--origin-to-force-quic-on=*')
    driver = webdriver.Chrome(options=opt, service=Service(ChromeDriverManager().install()))
    driver.get(domain)

    navigationStart = driver.execute_script("return window.performance.timing.navigationStart")
    responseStart = driver.execute_script("return window.performance.timing.responseStart")
    domComplete = driver.execute_script("return window.performance.timing.domComplete")

    firstbyte = responseStart - navigationStart
    loadtime = domComplete - responseStart

    driver.quit()

    return firstbyte, loadtime

# Function to append output of get_latency_ms to lists
def append_two(l1, l2, tuple):
    t1, t2 = tuple
    l1.append(t1)
    l2.append(t2)

def draw_cdf(vpn, naive, quicstep, bin_num, filename):
    vpn_values, vpn_base = np.histogram(vpn, bins = bin_num)
    vpn_cdf = np.cumsum(vpn_values / sum(vpn_values))

    naive_values, naive_base = np.histogram(naive, bins = bin_num)
    naive_cdf = np.cumsum(naive_values / sum(naive_values))

    quicstep_values, quicstep_base = np.histogram(quicstep, bins = bin_num)
    quicstep_cdf = np.cumsum(quicstep_values / sum(quicstep_values))

    plt.figure()
    plt.xlabel('Latency (ms)')
    plt.ylabel('Probability')
    plt.plot(vpn_base[1:], vpn_cdf, label='High Latency Secure Tunnel')
    plt.plot(naive_base[1:], naive_cdf, label='Censorship Vulnerable Native Link')
    plt.plot(quicstep_base[1:], quicstep_cdf, label='QUICstep Connection')
    plt.legend()
    plt.savefig(filename)

if __name__ == '__main__':
    vpn_firstbyte = []
    naive_firstbyte = []
    quicstep_firstbyte = []

    vpn_loadtime = []
    naive_loadtime = []
    quicstep_loadtime = []

    subprocess.run(['sudo', 'bash', 'setup.sh'])
  
    for i in range(NUM_REQUESTS):
        subprocess.run(['wg-quick', 'up', f'wg_qs'])
        append_two(quicstep_firstbyte, quicstep_loadtime, get_latency_ms(domain))
        subprocess.run(['wg-quick', 'down', f'wg_qs'])

        subprocess.run(['wg-quick', 'up', f'wg_vpn'])
        append_two(vpn_firstbyte, vpn_loadtime, get_latency_ms(domain))
        subprocess.run(['wg-quick', 'down', f'wg_vpn'])

        append_two(naive_firstbyte, naive_loadtime, get_latency_ms(domain))

    subprocess.run(['sudo', 'bash', 'takedown.sh'])

    for x in ['firstbyte', 'loadtime']:
        if x == 'firstbyte':
            vpn_latency = vpn_firstbyte
            naive_latency = naive_firstbyte
            quicstep_latency = quicstep_firstbyte
        else:
            vpn_latency = vpn_loadtime
            naive_latency = naive_loadtime
            quicstep_latency = quicstep_loadtime

        vpn_latency = np.array(vpn_latency)
        naive_latency = np.array(naive_latency)
        quicstep_latency = np.array(quicstep_latency)

        domain_filename = domain.replace('.', '')

        filename_vpn = f'{x}_vpn.csv'
        filename_naive = f'{x}_naive.csv'
        filename_quicstep = f'{x}_quicstep.csv'

        np.savetxt(filename_vpn, vpn_latency, fmt="%f", delimiter=",")
        np.savetxt(filename_naive, naive_latency, fmt="%f", delimiter=",")
        np.savetxt(filename_quicstep, quicstep_latency, fmt="%f", delimiter=",")
        
        filename = f'{x}.jpg'
        draw_cdf(vpn_latency, naive_latency, quicstep_latency, 50, filename)

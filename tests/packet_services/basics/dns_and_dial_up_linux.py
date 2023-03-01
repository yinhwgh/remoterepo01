#responsible: yanen.wang@thalesgroup.com
#location: Beijing
#TC0103934.001

import unicorn
import random
import platform
import os
import sys
import time
import re
import subprocess
import urllib.request
import urllib

from core.basetest import BaseTest
from os.path import dirname, realpath
from dstl.packet_domain.start_public_IPv4_data_connection import *
from dstl.auxiliary.ip_server.http_server import HttpServer
from dstl.auxiliary import init

def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
       per =100
    dstl.log.info ('%.2f%%' % per)
def download_file(url,dir):
    root = dirname(dirname(dirname(dirname(realpath(__file__)))))
    name = 'DLfile'
    dir = os.path.join(root, name)
    urllib.request.urlretrieve(url, dir, Schedule)
    urllib.request.urlcleanup()

class Test(BaseTest):
    """
            TC0103934.001  	DnsAndDialUpLinux
        """
    def __init__(self):
        super().__init__()
        self.dialup_conn_name = None

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.info("*** Test beginning ***")
        test.http_server = HttpServer("IPv4")
        server_ipv4_address = test.http_server.dstl_get_server_ip_address()
        test.expect(test.dut.dstl_start_public_ipv4_data_connection_over_dialup(test))
        test.sleep(20)
        test.get_ping_result(10, server_ipv4_address)
        test.log.info(" Downloading files ......")
        #download_file(test.http_server_url, dir)
        test.log.info("*** Stop dial up connection ***")
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test)
        test.sleep(20)
        test.dut.at1.send_and_verify('AT', 'OK')

    def get_ping_result(test, count, ip):
        command = 'ping -c %s' % count + " %s" % ip
        p = subprocess.Popen([command],
                             stdin=subprocess.PIPE,
                             stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)

        out = p.stdout.read().decode('utf-8')
        regex = r'.* time=.*ms'
        ping_results = re.findall(regex, out)
        ping_results.sort()
        index = int(0.1 * int(count))
        if len(ping_results) == 0:
            test.log.info("Error! No data!")
        elif len(ping_results) < index:
            test.log.info("Error! Index out of range!")
        else:
            test.log.info(ping_results)


def cleanup(test):
        test.dut.at1.send_and_verify('AT&F', 'OK')
        pass

if (__name__ == "__main__"):
    unicorn.main()

# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# test case:
# Debug version:SERVAL_300_032_UNICORN9B & MODS_Staging_V3.1.0_432

import unicorn
import re
from os.path import dirname, realpath
from core.basetest import BaseTest
from tests.device_management.iot_service_agent.mods_e2e_unicorn_performance_api import *
from dstl.auxiliary import init
from dstl.identification import get_imei
from dstl.usim import get_imsi
from dstl.auxiliary import restart_module
from dstl.hardware import set_real_time_clock
from dstl.auxiliary import check_urc
from dstl.auxiliary.restart_module import dstl_restart
from dstl.packet_domain import start_public_IPv4_data_connection


import json
import datetime


class Test(BaseTest):
    """
    Use Case:
    """
    iccids = [''] * 100
    time_consumption_dict = {'register device': [0] * 100, 'download profile': [0] * 100, 'trigger restart': [0] * 100,
                             'register network': [0] * 100}
    
    def setup(test):
        test.cmw500_network=True
        setup_for_provision_or_swich(test)
        test.log.step('[Setup]-End.Fallback to operational profile 1.')
        fallback_to_original_operational_profile(test, step='[Setup]-End')
        return
    
    def run(test):
        test.log.info('*' * 80)
        test.log.step(f'Connectivity switch with ppp download')
        test.log.info('*' * 80)
        test.connectivity_switch_with_ppp_download()
        return
    
    def connectivity_switch_with_ppp_download(test):
        for i in range(1, 21):
            test.log.info('*' * 80)
            test.log.step(f'***Loop {i}/20')
            test.log.info('*' * 80)
            test.log.step(f"[i={i}] Step 1. Configure module before connectivity switch.")
            test.expect(connectivity_switch_module_configure(test, step=1))
            test.log.step(f"[i={i}] Step 2. Register to network, rat={test.rat}")
            test.expect(register_network(test))
            test.log.step(f"[i={i}] Step 3. Launch data download through dial up.")
            test.thread(big_data_download_via_ppp,test)
            test.sleep(40)
            test.log.step(f"[i={i}] Step 4. Record time consumption during connectivity switch.")
            test.expect(record_time_consumption(test, test.time_consumption_dict, i))
            test.expect(record_iccid_switch(test, test.iccids, i))
            test.log.step(f"[i={i}] Step 5. Restore steps.")
            test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, "Dial-up Connection")
            test.expect(fallback_to_original_operational_profile(test, step=5))
            print_time_consumption_report(test, 'Connectivity_Switch', test.iccids, test.time_consumption_dict)

        return
    
    def cleanup(test):
        test.dut.dstl_stop_public_ipv4_data_connection_over_dialup(test, "Dial-up Connection")
        print_time_consumption_report(test, 'Connectivity_Switch', test.iccids, test.time_consumption_dict)
        test.log.info('Drop all broken subscriptions and create them again.')
        cleanup_broken_iccids(test)
        return

def big_data_download_via_ppp(test):
    test.log.info('Dialup')
    test.expect(diaup(test))
    test.log.info('Download a big fie.')
    download_file(test)
    return True

def diaup(test):
    if test.dut.dstl_start_public_ipv4_data_connection_over_dialup_multiple(test, "at2", "Dial-up Connection"):
        test.dialup_start=True
        return True
    else:
        test.dialup_start = False
        return False

def Schedule(a,b,c):
    per = 100.0 * a * b / c
    if per > 100:
       per =100
    time.sleep(2)
    dstl.log.info ('%.2f%%' % per)

def download_file(test):
    #url='ftp://speedtest.tele2.net/1GB.zip'
    url='ftp://192.168.99.196/ftp_anon/300M.zip'
    root = dirname(dirname(dirname(realpath(__file__))))
    name = 'DLFile_E2E'
    dir = os.path.join(root, name)
    try:
        urllib.request.urlretrieve(url, dir, Schedule)
        urllib.request.urlcleanup()
    except:
        test.log.info('Big data download via ppp is stopped due to connection is aborted.')
        urllib.request.urlcleanup()
if "__main__" == __name__:
    unicorn.main()

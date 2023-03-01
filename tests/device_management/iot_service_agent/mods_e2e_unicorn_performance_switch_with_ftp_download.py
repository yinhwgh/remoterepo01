# responsible: jingxin.shen@thalesgroup.com
# location: Beijing
# test case:
# Debug version:SERVAL_300_032_UNICORN9B & MODS_Staging_V3.1.0_432

import unicorn
import re
import json
import datetime
import random
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
from dstl.auxiliary.ip_server.ftp_server import FtpServer
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.profile_storage.dstl_check_siss_read_response import dstl_check_siss_read_response
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs




class Test(BaseTest):
    """
    Use Case:
    """
    iccids = [''] * 100
    time_consumption_dict = {'register device': [0] * 100, 'download profile': [0] * 100, 'trigger restart': [0] * 100,
                             'register network': [0] * 100}
    
    def setup(test):
        test.cmw500_network = True
        setup_for_provision_or_swich(test)
        test.log.step('[Setup]-End.Fallback to operational profile 1.')
        fallback_to_original_operational_profile(test, step='[Setup]-End')
        return
    
    def run(test):
        test.log.info('*' * 80)
        test.log.step(f'Connectivity switch with ftp download')
        test.log.info('*' * 80)
        test.connectivity_switch_with_ftp_download()
        return
    
    def connectivity_switch_with_ftp_download(test):
        for i in range(1, 21):
            test.log.info('*' * 80)
            test.log.step(f'***Loop {i}/20')
            test.log.info('*' * 80)
            test.log.step(f"[i={i}] Step 1. Configure module before connectivity switch.")
            test.expect(connectivity_switch_module_configure(test, step=1))
            test.log.step(f"[i={i}] Step 2. Register to network, rat={test.rat}")
            test.expect(register_network(test))
            test.log.step(f"[i={i}] Step 3. Launch data download through dial up.")
            test.thread(big_data_download_via_ftp,test)
            test.log.step(f"[i={i}] Step 4. Record time consumption during connectivity switch.")
            test.expect(record_time_consumption(test, test.time_consumption_dict, i))
            test.expect(record_iccid_switch(test, test.iccids, i))
            test.log.step(f"[i={i}] Step 5. Restore steps.")
            test.expect(fallback_to_original_operational_profile(test, step=5))
            print_time_consumption_report(test, 'Connectivity_Switch', test.iccids, test.time_consumption_dict)

        return
    
    def cleanup(test):
        print_time_consumption_report(test, 'Connectivity_Switch', test.iccids, test.time_consumption_dict)
        test.log.info('Drop all broken subscriptions and create them again.')
        cleanup_broken_iccids(test)
        return

def big_data_download_via_ftp(test):
    test.log.info("[Donload_via_FTP] 1.Define FTP fget profile.")
    test.dut.dstl_set_scfg_tcp_with_urcs("on",device_interface='at2')
    test.dut.at2.send_and_verify('at^sica=1,1','OK')
    test.dut.at2.send_and_verify('at^sisc=0', 'OK')
    test.ftp_fget = FtpProfile(test.dut, 0, 1, device_interface='at2',srv_type="Ftp",command="fget", alphabet="1",
                               host="192.168.99.196", ftpath='/ftp_anon/',files="1M.log",user="thales",passwd='abc')
    test.ftp_fget.dstl_generate_address()
    test.expect(test.ftp_fget.dstl_get_service().dstl_load_profile())
    while True:
        test.log.step("[Donload_via_FTP] 5. Repeat 2-3")
        test.log.step("[Donload_via_FTP] 2. Open the defined profile")
        if not test.ftp_fget.dstl_get_service().dstl_open_service_profile(urc_timeout=180):
            test.log.info('Big data download via ftp is stopped due to connection is aborted.')
            return True

        test.log.step("[Donload_via_FTP] 3. Close the defined service profile")
        test.expect(test.ftp_fget.dstl_get_service().dstl_close_service_profile())





if "__main__" == __name__:
    unicorn.main()

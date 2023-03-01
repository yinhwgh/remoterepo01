# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105516.001 - SmartMeter_downloadConfigurationFile_normalFlow
# Hints:
# Some parameters should be defined in local.cfg currently,such as ftps_server,ftps_user and etc.

import unicorn
import time
import datetime
import re
import os
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(False)

    def run(test):

        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        smart_meter_init_module_normal_flow.set_listener_mode(False)
        download_configuration_file_normal_flow(test)

    def cleanup(test):
        pass

def download_configuration_file_normal_flow(test,sftpes=True,expect_dcd_active=False):
    test.log.info('*** download_configuration_file_normal_flow begin ***')
    global ftpes, ipVersion
    ftpes = sftpes
    ipVersion = "4"
    test.log.step('NF-01: Check for listener mode')
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            if expect_dcd_active is False:
                test.log.error('Expect DCD line is inactive here!')
                test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
            return True
        else:
            if expect_dcd_active is True:
                test.log.error('Expect DCD line is active here!')
            time.sleep(5)
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-01: Check for listener mode with DCD checking and closing listener', True)
    else:
        test.dut.dstl_collect_result('NF-01: Check for listener mode without operation of DCD checking and closing listener', True)

    test.log.step('NF-02: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-02: Close, configure and restart the IP service bearer 1.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_init_module_normal_flow.restart_ip_service_bearer, smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-03: Switch on the IP URCs)')
    test.dut.dstl_collect_result('NF-03: Switch on the IP URCs)', test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0")))

    test.log.step('NF-04: Close and configure IP service profile 1 as FTPS or FTPES client.')
    test.dut.dstl_collect_result('NF-04: Close and configure IP service profile 1 as FTPS or FTPES client.',
                                 smart_meter_init_module_normal_flow.retry(test, configure_open_FTPS_client, smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-05: Download the configuration data file in 1000 Byte blocks and the size of the configuration '
                  'data file is up to 12 kBytes.')
    test.dut.dstl_collect_result('NF-05: Download the configuration data file in 1000 Byte blocks and the size of the configuration data file is up to 12 kBytes',download_configuration_data_file(test))

    test.log.step('NF-06: Switch off the IP URCs.')
    test.dut.dstl_collect_result('NF-06: Switch off the IP URCs.', test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","off"', ".*OK|.*0")))

    test.log.step('NF-07: Check for listener mode')
    if smart_meter_init_module_normal_flow.get_run_all() == True:
        smart_meter_init_module_normal_flow.set_listener_mode(True)
        if smart_meter_init_module_normal_flow.check_listener_mode(test) == True:
            test.dut.dstl_collect_result('NF-07: Check for listener mode during duration test--It should be true and got to UC ProvideDataConnection', True)
            return True
    elif smart_meter_init_module_normal_flow.get_run_all() == False:
        if smart_meter_init_module_normal_flow.check_listener_mode(test):
            if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
                return
            else:
                smart_meter_init_module_normal_flow.close_listener(test)
                test.dut.dstl_collect_result('NF-07: Check for listener mode with DCD checking and closing listener', True)
        else:
            test.dut.dstl_collect_result('NF-07: Check for listener mode without operation of DCD checking and closing listener', True)

    test.dut.dstl_print_results()
    test.log.info('*** download_configuration_file_normal_flow end ***')

    return True

def configure_open_FTPS_client(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=1", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object()
    con_id = connection_setup_dut.dstl_get_used_cid()

    global ftps_client
    if ipVersion == "4":
        ftps_client = FtpProfile(test.dut, srv_profile_id=1, con_id=con_id, command='get', host=test.ftps_server_ipv4, ip_version=ipVersion,
                                     user=test.ftps_username_ipv4, passwd=test.ftps_password_ipv4, files=test.ftp_files,
                                    secopt=1, secure_connection=True, ftpes=ftpes)
    elif ipVersion == "6":
        ftps_client = FtpProfile(test.dut, srv_profile_id=1, con_id=con_id, command='get', host=test.ftps_server_ipv6, ip_version=ipVersion,
                                     user=test.ftps_username_ipv6, passwd=test.ftps_password_ipv6, files=test.ftp_files,
                                    secopt=1, secure_connection=True, ftpes=ftpes)

    ftps_client.dstl_generate_address()
    ftps_client.dstl_get_service().dstl_load_profile()
    ftps_client.dstl_get_service().dstl_open_service_profile()
    if ipVersion == "4":
        ftps_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                   '"Ftp connect {}:{}"'.format(test.ftps_server_ipv4,
                                                                                                test.ftps_server_port_ipv4))
    elif ipVersion == "6":
        ftps_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                   '"Ftp connect {}:{}"'.format(test.ftps_server_ipv6,
                                                                                                test.ftps_server_port_ipv6))
    result = result & test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
    test.sleep(2)

    return result

def download_configuration_data_file(test):
    result = True
    number = 12
    for i in range(1, number+1):
        test.log.info(
            '************************ Download data for ' + str(i) + ' times *****************************')
        ftps_client.dstl_get_service().dstl_read_return_data(1000, timeout=0.5)
        # rx_counter_value = ftps_client.dstl_get_parser().dstl_get_service_data_counter("rx")
        result = result & test.expect(test.dut.at1.send_and_verify("AT^SISO?", ".*OK.*|.*0.*"))

    return result


if "__main__" == __name__:
    unicorn.main()

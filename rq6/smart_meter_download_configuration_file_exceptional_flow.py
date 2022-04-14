# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105518.001 - SmartMeter_downloadConfigurationFile_exceptionalFlow
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
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)


    def run(test):

        download_configuration_file_exceptional_flow(test)

    def cleanup(test):
        pass

def download_configuration_file_exceptional_flow(test,sftpes=False):
    test.log.info('*** download_configuration_file_exceptional_flow begin ***')
    global ftpes
    ftpes = sftpes
    test.log.step('Preparation for triggering NF-02 failure')
    smart_meter_init_module_normal_flow.mc_remove_sim(test)
#    smart_meter_init_module_normal_flow.mc_deregister_network(test)
    time.sleep(3)

    test.log.step('NF-01: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong. Script stops.')
        test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-01: Check for listener mode', True)

    test.log.step('NF-02: Close, configure and restart the IP service bearer 1.')
    test.log.step('NF-03: Power down the module.')
    test.log.step('NF-04: Wait a security time about 5 seconds.')
    test.log.step('NF-05: Boot up the module via the ignition line and re-initialized module.')
#    test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", '^0\r\n$'))
    test.dut.dstl_collect_result('NF-02---NF-05',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_init_module_normal_flow.restart_ip_service_bearer, smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-06: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong.')
        test.dut.dstl_collect_result('NF-06: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-06: Check for listener mode', True)

    test.log.step('NF-07: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-07: Close, configure and restart the IP service bearer 1.',
        test.expect(smart_meter_init_module_normal_flow.restart_ip_service_bearer(test)))

    test.log.step('NF-08: Switch on the IP URCs)')
    test.dut.dstl_collect_result('NF-08: Switch on the IP URCs)', test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK.*|.*0.*")))

    test.log.step('Preparation for triggering NF-09 failure')
    smart_meter_init_module_normal_flow.mc_remove_sim(test)
#    smart_meter_init_module_normal_flow.mc_deregister_network(test)

    test.log.step('NF-09: Close and configure IP service profile 1 as FTPS or FTPES client.')
    test.log.step('NF-10: Power down the module.')
    test.log.step('NF-11: Wait a security time about 5 seconds.')
    test.log.step('NF-12: Boot up the module via the ignition line and re-initialized module.')
#    test.expect(test.dut.at1.send_and_verify("AT+CGATT=0", '^0\r\n$'))
    test.dut.dstl_collect_result('NF-09---NF-12',
                                 smart_meter_init_module_normal_flow.retry(test, configure_open_FTPS_client, smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-13: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong. Script stops.')
        test.dut.dstl_collect_result('NF-13: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-13: Check for listener mode', True)

    test.log.step('NF-14: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-14: Close, configure and restart the IP service bearer 1.',
        test.expect(smart_meter_init_module_normal_flow.restart_ip_service_bearer(test)))

    test.log.step('NF-15: Switch on the IP URCs)')
    test.dut.dstl_collect_result('NF-15: Switch on the IP URCs)', test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK.*|.*0.*")))

    test.log.step('NF-16: Close and configure IP service profile 1 as FTPS or FTPES client.')
    test.dut.dstl_collect_result('NF-16: Close and configure IP service profile 1 as FTPS or FTPES client.', test.expect(configure_open_FTPS_client(test)))

    test.log.step('NF-17: Download the configuration data file in 1000 Byte blocks and the size of the configuration '
                  'data file is up to 12 kBytes.')
    test.dut.dstl_collect_result('NF-17: Download the configuration data file in 1000 Byte blocks and the size of the configuration '
                  'data file is up to 12 kBytes.', test.expect(download_configuration_data_file(test)))

    test.log.step('NF-18: Switch off the IP URCs.')
    test.dut.dstl_collect_result('NF-18: Switch off the IP URCs.', test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","off"', ".*OK|.*0")))

    test.log.step('NF-19: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        smart_meter_init_module_normal_flow.close_listener(test)
        test.dut.dstl_collect_result('NF-19: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-19: Check for listener mode', True)

    test.dut.dstl_print_results()
    test.log.info('*** download_configuration_file_exceptional_flow end ***')
    return True

def configure_open_FTPS_client(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=1", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object()
    con_id = connection_setup_dut.dstl_get_used_cid()
    global ftps_client
    ftps_client = FtpProfile(test.dut, srv_profile_id=1, con_id=con_id, command='get', host=test.ftps_server_ipv4,
                            user=test.ftps_username_ipv4, passwd=test.ftps_password_ipv4, files=test.ftp_files,
                            secopt=1, secure_connection=True,ftpes=ftpes)
    ftps_client.dstl_generate_address()
    ftps_client.dstl_get_service().dstl_load_profile()

    ftps_client.dstl_get_service().dstl_open_service_profile()
    ftps_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                   '"Ftp connect {}:{}"'.format(test.ftps_server_ipv4,
                                                                                                test.ftps_server_port_ipv4))
    result = result & test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
    test.sleep(2)

    test.log.info('*** Download configuration file alternative flow end ***')
    return result

def download_configuration_data_file(test):
    result = True
    number = 12
    for i in range(1, number+1):
        test.log.info(
            '************************ Download data for ' + str(i) + ' times *****************************')
        ftps_client.dstl_get_service().dstl_read_return_data(1000,timeout=2)
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISO?", ".*OK.*|.*0.*"))
#    result = result & test.expect(ftps_client.dstl_get_parser().dstl_get_service_state() -= ServiceState.UP.value)

    return result


if "__main__" == __name__:
    unicorn.main()

# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105503.001 - SmartMeter_updateApplication_alternativeFlow

# Hints:
# Some parameters should be defined in local.cfg currently,such as ftps_server,ftps_user and etc.

# Intention:
# The case is intended to test the alternative flow of downloading the updated firmware version
# and restarting using the new one according to RQ600042.001.

import unicorn
import time
import datetime
import re
import os
import random
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from dstl.internet_service.profile.ftp_profile import FtpProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        pass

    def run(test):

        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        update_application_alternative_flow(test)

    def cleanup(test):
        pass

def update_application_alternative_flow(test, sftpes=True):
    test.log.info('*** download_update_application_alternative_flow begin ***')
    global ftpes
    ftpes = sftpes
    test.log.step('Preparation for triggering NF-02: Define and open TCP listener service.')

    test.expect(test.dut.at1.send_and_verify("ATV1", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object(ip_public=True)
    socket_listener = SocketProfile(test.dut, "2", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                    host="listener", localport=65100)
    socket_listener.dstl_generate_address()
    test.expect(socket_listener.dstl_get_service().dstl_load_profile())

    test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
    test.dut.dstl_collect_result('Preparation for triggering NF-02: Define and open TCP listener service.', test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n")))
    test.sleep(2)
    test.expect(test.dut.at1.send_and_verify("ATV0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))

    test.log.step('NF-01: Check for listener mode')
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.dut.dstl_collect_result('NF-01: Check for listener mode', True)
        result = True
        test.log.step(
            'NF-02: Check the DCD line for an ongoing data transmission.Repeat it until the DCD line becomes inactive.')
        while (result):
            if smart_meter_init_module_normal_flow.check_dcd_line(test) is False:
                break
        test.dut.dstl_collect_result(
            'NF-02: Check the DCD line for an ongoing data transmission.Repeat it until the DCD line becomes inactive.',
            True)

        test.log.step('NF-03: Close the listener')
        if smart_meter_init_module_normal_flow.close_listener(test) == False:
            test.log.error('Close the listener is failed.')
            test.dut.dstl_collect_result('NF-03: Close the listener', False)
            os._exit(1)
        test.dut.dstl_collect_result('NF-03: Close the listener', True)
    else:
        test.dut.dstl_collect_result('NF-01: Check for listener mode', False)

    test.log.step('NF-04: Close, configure and restart the IP service bearer 1.')
    test.dut.dstl_collect_result('NF-04: Close, configure and restart the IP service bearer 1.', test.expect(smart_meter_init_module_normal_flow.restart_ip_service_bearer(test)))

    test.log.step('NF-05: Switch on the IP URCs)')
    test.dut.dstl_collect_result('NF-05: Switch on the IP URCs', test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0")))

    test.log.step('NF-06: Close and configure IP service profile 1 as FTPS or FTPES client.')
    test.dut.dstl_collect_result('NF-06: Close and configure IP service profile 1 as FTPS or FTPES client.', test.expect(configure_open_FTPS_client(test)))

    test.log.step('NF-07: Download the application firmware file (about 400-450KBytes) in 1000 Bytes blocks.')
    test.dut.dstl_collect_result(
        'NF-07: Download the application firmware file (about 400-450KBytes) in 1000 Bytes blocks.', test.expect(download_update_application_file(test)))

    test.log.step('NF-08: Switch off the IP URCs.')
    test.dut.dstl_collect_result('NF-08: Switch off the IP URCs.',test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","off"', ".*OK|.*0")))

    test.log.step('NF-09: Switch off the module.')
    test.log.step('NF-10: Restart its new firmware.')
    test.log.step('NF-11: Re-intialize the module.')
    smart_meter_init_module_normal_flow.AF_A_restart(test)
    test.dut.dstl_collect_result('NF09--NF11', True)

    test.dut.dstl_print_results()
    test.log.info('*** download_update_application_alternative_flow end ***')
    return True


def configure_open_FTPS_client(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=1", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object()
    con_id = connection_setup_dut.dstl_get_used_cid()
    global ftps_client
    ftps_client = FtpProfile(test.dut, srv_profile_id=1, con_id=con_id, command='get', host=test.ftps_server_ipv4,
                            user=test.ftps_username_ipv4, passwd=test.ftps_password_ipv4, files=test.ftp_files,
                            secopt=1, secure_connection=True, ftpes=ftpes)
    ftps_client.dstl_generate_address()
    ftps_client.dstl_get_service().dstl_load_profile()

    ftps_client.dstl_get_service().dstl_open_service_profile()
    ftps_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "2100",
                                                                   '"Ftp connect {}:{}"'.format(test.ftps_server_ipv4,
                                                                                                test.ftps_server_port_ipv4))
    result = result & test.expect(ftps_client.dstl_get_urc().dstl_is_sisr_urc_appeared(1))
    test.sleep(2)

    return result

def download_update_application_file(test):
    result = True
    number = random.randint(400, 450)
    for i in range(1, number+1):
        test.log.info(
            '************************ Download data for ' + str(i) + ' times *****************************')
        ftps_client.dstl_get_service().dstl_read_return_data(1000,timeout=2)
    test.expect(test.dut.at1.send_and_verify("AT^SISO?", ".*OK.*|.*0.*"))
    return result

if "__main__" == __name__:
    unicorn.main()

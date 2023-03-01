# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105502.001 - SmartMeter_sendAlertMessage_alternativeFlow
# Hints:
# Some parameters should be defined in local.cfg currently,such as SIM1,SIM2,ftps_server and etc.

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
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(False)
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)


    def run(test):
        test.log.step('Preparation: Register network.')

        send_alert_message_alternative_flow(test)

    def cleanup(test):
        pass

def send_alert_message_alternative_flow(test):
    test.log.info('*** send_alert_message_alternative_flow begin ***')

    global SIM1, SIM2
    SIM1 = test.SIM1
    SIM2 = test.SIM2

    test.log.step('Preparation for triggering NF-02: Define and open TCP listener service.')

    test.expect(test.dut.at1.send_and_verify("ATV1", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object(ip_public=True)
    test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

    socket_listener = SocketProfile(test.dut, "2", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                    host="listener", localport=65100)
    socket_listener.dstl_generate_address()
    test.expect(socket_listener.dstl_get_service().dstl_load_profile())

    test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
    test.dut.dstl_collect_result('Preparation for triggering NF-02: Define and open TCP listener service.',test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n")))
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

    test.log.step('NF-04: Send the message to the first message receiver.')
    test.dut.dstl_collect_result('NF-04: Send the message to the first message receiver.', test.expect(send_short_message1(test)))

    test.log.step('NF-05: Send the message to the second message receiver.')
    test.dut.dstl_collect_result('NF-04: Send the message to the first message receiver.',test.expect(send_short_message2(test)))

    test.log.step('NF-06: Shut down the module')
    test.dut.dstl_collect_result('NF-06: Shut down the module', test.expect(test.dut.at1.send_and_verify("AT^SMSO", ".*OK|.*0")))

    test.dut.dstl_print_results()
    test.log.info('*** send_alert_message_alternative_flow end ***')
    return True


def send_short_message1(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMGF=1", ".*OK.*|.*0.*"))
#    test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.int_voice_nr), ".*>.*"))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.int_voice_nr), ".*>.*"))
    result = result & test.expect(
        test.dut.at1.send_and_verify('Send short message', end="\u001A", expect=r"\+CMGS: \d{1,3}(.*OK.*|.*0.*)", timeout=20))

    return result

def send_short_message2(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMGF=1", ".*OK.*|.*0.*"))
#    test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.dut.sim.int_voice_nr), ".*>.*"))
    result = result & test.expect(test.dut.at1.send_and_verify("AT+CMGS=\"{}\"".format(test.r1.sim.int_voice_nr), ".*>.*"))
    result = result & test.expect(
        test.dut.at1.send_and_verify('Send short message', end="\u001A", expect=r"\+CMGS: \d{1,3}(.*OK.*|.*0.*)", timeout=20))

    return result


if "__main__" == __name__:
    unicorn.main()

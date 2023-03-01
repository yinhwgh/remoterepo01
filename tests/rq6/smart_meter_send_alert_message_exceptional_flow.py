# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105511.001 - SmartMeter_sendAlertMessage_exceptionalFlow
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
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(False)
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)


    def run(test):

        send_alert_message_exceptional_flow(test)

    def cleanup(test):
        pass

def send_alert_message_exceptional_flow(test):
    test.log.info('*** Send alert message exceptional flow begin ***')

    test.log.step('Preparation for triggering NF-02 failure')
    smart_meter_init_module_normal_flow.mc_deregister_network(test)

    test.log.step('NF-01: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong. Script stops.')
        test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-01: Check for listener mode', True)

    test.log.step('NF-02: Send the message to the first message receiver and the 3 repetitions are failed.')
    test.log.step('NF-03: Power down the module.')
    test.log.step('NF-04: Wait a security time about 5 seconds.')
    test.log.step('NF-05: Boot up the module via the ignition line and re-initialized module.')
#    smart_meter_init_module_normal_flow.retry(test, send_short_message, smart_meter_init_module_normal_flow.AF_A_restart, 3)\
#     smart_meter_init_module_normal_flow.retry(test, send_short_message,
#                                               smart_meter_init_module_normal_flow.uc_init_module, 3)
    test.dut.dstl_collect_result('NF-02---NF-05', smart_meter_init_module_normal_flow.retry(test, send_short_message1,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-06: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        test.log.error('Listener mode is wrong. Script stops.')
        test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
        os._exit(1)
    test.dut.dstl_collect_result('NF-01: Check for listener mode', True)

    test.log.step('NF-07: Send the message to the first message receiver.')
    test.dut.dstl_collect_result('NF-07: Send the message to the first message receiver.', test.expect( send_short_message1(test)))
    test.log.step('Preparation for triggering NF-08 failure')
    smart_meter_init_module_normal_flow.mc_deregister_network(test)

    test.log.step('NF-08: Send the message to the second message receiver and the 3 repetitions are failed.')
    test.log.step('NF-09: Power down the module.')
    test.log.step('NF-10: Wait a security time about 5 seconds.')
    test.log.step('NF-11: Boot up the module via the ignition line and re-initialized module.')
#    smart_meter_init_module_normal_flow.retry(test, send_short_message, smart_meter_init_module_normal_flow.AF_A_restart, 3)
    test.dut.dstl_collect_result('NF-08---NF11', smart_meter_init_module_normal_flow.retry(test, send_short_message2,
                                                                 smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-12: Send the message to the second message receiver.')
    test.dut.dstl_collect_result('NF-12: Send the message to the second message receiver.', test.expect(send_short_message2(test)))

    test.log.step('NF-13: Shut down the module')
    test.dut.dstl_collect_result('NF-13: Shut down the module', test.expect(test.dut.at1.send_and_verify("AT^SMSO", ".*OK|.*0")))

    time.sleep(5)
    test.dut.dstl_print_results()
    test.log.info('*** Send alert message exceptional flow end ***')
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

# def retry(test, fun_name, error_handling, retry_counter):
#     while (retry_counter > 0):
#         if fun_name(test) is True:
#             break
#         else:
#             retry_counter = retry_counter - 1
#     if retry_counter == 0:
#         error_handling(test)
#         return False
#     return None

if "__main__" == __name__:
    unicorn.main()

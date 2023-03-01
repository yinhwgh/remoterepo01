# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0105509.001 - SmartMeter_sendAlertMessage_normalFlow
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
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(False)


    def run(test):
        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        send_alert_message_normal_flow(test)

    def cleanup(test):
        pass

def send_alert_message_normal_flow(test):

    test.log.info('*** send_alert_message_normal_flow begin ***')

    test.log.step('NF-01: Check for listener mode.')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-01: Check for listener mode', True)

    test.log.step('NF-02: Send the message to the first message receiver.')
#    test.dut.dstl_collect_result('NF-02: Send the message to the first message receiver.', test.expect(send_short_message(test, test.SIM1)))
    test.dut.dstl_collect_result('NF-02: Send the message to the first message receiver.', smart_meter_init_module_normal_flow.retry(test, send_short_message1,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-03: Send the message to the second message receiver.')
    test.dut.dstl_collect_result('NF-02: Send the message to the second message receiver.', smart_meter_init_module_normal_flow.retry(test, send_short_message2,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    if smart_meter_init_module_normal_flow.get_run_all() == False:
        test.log.step('NF-04: Shut down the module.')
        test.dut.dstl_collect_result('NF-04: Shut down the module.', test.expect(test.dut.at1.send_and_verify("AT^SMSO", ".*OK|.*0")))
    elif smart_meter_init_module_normal_flow.get_run_all() == True:
        time.sleep(5)
        test.log.step('NF-04: Init module step NF-02.')
        test.dut.dstl_collect_result('NF-04: Init module step NF-02',
                                     smart_meter_init_module_normal_flow.AF_A_restart(test))

    test.dut.dstl_print_results()
    test.log.info('*** send_alert_message_normal_flow end ***')
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

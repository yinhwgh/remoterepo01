# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0107174.001 - SmartMeter_sendAlertMessage_send_second_SMS_error_exceptionalFlowA_update
# Hints:
# Some parameters should be defined in local.cfg currently,such as ftps_server_ipv4 and etc.

import unicorn
import time
import re
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_send_alert_message_normal_flow_update
from tests.rq6 import smart_meter_send_alert_message_alternativeFlowB_update
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.internet_service.parser.internet_service_parser import ServiceState

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(True)

    def run(test):

        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        send_alert_message_send_second_SMS_error_exceptional_flowA_update(test)

    def cleanup(test):
        pass

def send_alert_message_send_second_SMS_error_exceptional_flowA_update(test):

    global tamperingAttempt_status, glitch_status, power_loss
    tamperingAttempt_status = False
    glitch_status = False
    power_loss = False

    test.log.info('*** send_alert_message_send_second_SMS_error_exceptional_flowA_update begin ***')
    test.dut.at1.reconfigure({"rtscts": False})

    test.log.step('NF-01: Check for listener mode.')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-01: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-01: Check for listener mode', True)

    test.log.step('NF-02: Check if tampering attempt.')
    tamperingAttempt_status = False
    test.dut.dstl_collect_result('NF-02: Check if tampering attempt.', True)

    test.log.step('NF-03: Send the module to sleep.')
    enable_power_saving_mode(test)
    test.expect(test.dut.at1.send_and_verify("AT\Q 0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    test.dut.dstl_collect_result('NF-03: Send the module to sleep.', smart_meter_init_module_normal_flow.retry(test, check_enter_sleep,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-04: Check if really power loss or only a glitch for 9 seconds.')
    time.sleep(9)
    test.dut.dstl_collect_result('NF-04: Check if really power loss or only a glitch for 9 seconds.', True)

    test.log.step('NF-05:  Wake up the module.')
    test.dut.dstl_collect_result('NF-05:  Wake up the module.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_normal_flow_update.wake_up_module,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))
    test.log.step('NF-06: disables power saving.')
    test.dut.dstl_collect_result('NF-06: disables power saving.',
                                 smart_meter_init_module_normal_flow.retry(test, disable_power_saving_mode,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-07: Configure the SMS parameters.')
    test.dut.dstl_collect_result('NF-07: Configure the SMS parameters.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.configure_SMS,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))


    test.log.step('NF-08:  Send the alert as short message.')
    test.dut.dstl_collect_result('NF-08: Configure the first UDP socket.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.send_short_message1,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-09: Check if power loss.')
    power_loss = False
    test.dut.dstl_collect_result('NF-09: Check if power loss.', True)

    test.log.step('NF-10: Configure the second SMS.')
    test.dut.dstl_collect_result('NF-10: Configure a second SMS.', smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.configure_SMS,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('Perepare for trigger error')
    smart_meter_init_module_normal_flow.mc_remove_sim(test)

    test.log.step('NF-11: Send the alert as short message to a second server.')
    test.log.step('NF-12: Shut down the module via at^smso.')
    test.log.step('NF-13: Wait a security time about 5 seconds.')
    test.log.step('NF-14: Boot up the module via the ignition line and re-initialized module.')
    test.dut.dstl_collect_result('NF-11: Send the alert as short message to a second server.\n'
                                 'NF-12: Shut down the module via at^smso.\n'
                                 'NF-13: Wait a security time about 5 seconds.\n'
                                 'NF-14: Boot up the module via the ignition line and re-initialized module.',
                                 smart_meter_init_module_normal_flow.retry(test,smart_meter_send_alert_message_alternativeFlowB_update.send_short_message2,
                                                                     smart_meter_init_module_normal_flow.AF_A_restart,
                                                                     3))

    test.dut.at1.reconfigure({"rtscts": False})
    test.log.step('NF-15: Repeat step1-11 --- NF-01: Check for listener mode.')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-01: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-01: Check for listener mode', True)

    test.log.step('NF-15: Repeat step1-11 --- NF-02: Check if tampering attempt.')
    tamperingAttempt_status = False
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-02: Check if tampering attempt.', True)

    test.log.step('NF-15: Repeat step1-11 --- NF-03: Send the module to sleep.')
    enable_power_saving_mode(test)
    test.expect(test.dut.at1.send_and_verify("AT\Q 0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-03: Send the module to sleep.',
                                 smart_meter_init_module_normal_flow.retry(test, check_enter_sleep,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-15: Repeat step1-11 --- NF-04:  Check if really power loss or only a glitch for 9 seconds.')
    time.sleep(9)
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-04:  Check if really power loss or only a glitch for 9 seconds.', True)

    test.log.step('NF-15: Repeat step1-11 --- NF-05:  Wake up the module.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-05:  Wake up the module.',
                                 smart_meter_init_module_normal_flow.retry(test,
                                                                           smart_meter_send_alert_message_normal_flow_update.wake_up_module,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))
    test.log.step('NF-15: Repeat step1-11 --- NF-06: disables power saving.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-06: disables power saving.',
                                 smart_meter_init_module_normal_flow.retry(test, disable_power_saving_mode,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-15: Repeat step1-11 --- NF-07: Configure the SMS parameters.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-07: Configure the SMS parameters.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.configure_SMS,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-15: Repeat step1-11 --- NF-08:  Send the alert as short message.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-08: Configure the first UDP socket',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.send_short_message1,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-15: Repeat step1-11 --- NF-08:  Send the alert as short message.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-08: Configure the first UDP socket',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.send_short_message1,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-15: Repeat step1-11 --- NF-09: Check if power loss.')
    power_loss = False
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-09: Check if power loss.', True)

    test.log.step('NF-15: Repeat step1-11 --- NF-10: Configure the second SMS.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-10: Configure a second SMS.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.configure_SMS,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-15: Repeat step1-11 --- NF-11: Send the alert as short message to a second server.')
    test.dut.dstl_collect_result('NF-15: Repeat step1-11 --- NF-11: Send the alert as short message to a second server.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_alternativeFlowB_update.send_short_message2,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-16: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        smart_meter_init_module_normal_flow.close_listener(test)
        test.dut.dstl_collect_result('NF-16: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-16: Check for listener mode', True)

    test.dut.dstl_print_results()
    test.log.info('*** send_alert_message_send_second_SMS_error_exceptional_flowA_update end ***')
    return True

def enable_power_saving_mode(test):
    global power_save_period, power_save_wakeup
    power_save_period = 52
    power_save_wakeup = 50
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PwrSave","enabled","'+str(power_save_period)+'","' + str(power_save_wakeup) + '"', ".*OK.*|.*0.*"))
    return result

def disable_power_saving_mode(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify(
        'AT^SCFG="MEopMode/PwrSave","disabled","' + str(power_save_period) + '","' + str(power_save_wakeup) + '"',
        ".*OK.*|.*0.*"))
    return result

def check_enter_sleep(test):
    sleep_status = False
    result = True
    sStartTime = time.time()
    result = result & test.dut.devboard.send_and_verify('MC:URC=SER', 'OK')
    while time.time() - sStartTime < power_save_period/10:
        if re.match('.*>URC:  CTS0: 1.*', test.dut.devboard.last_response, re.DOTALL):
            result = result & True
            test.log.info('Module is in sleep mode.')
            sleep_status = True
            break
        else:
            test.dut.devboard.read(append=False)
    if sleep_status == False and time.time() - sStartTime >= power_save_period/10:
        result = result & False
        test.log.error('Module is not in sleep mode.')

    return result


if "__main__" == __name__:
    unicorn.main()

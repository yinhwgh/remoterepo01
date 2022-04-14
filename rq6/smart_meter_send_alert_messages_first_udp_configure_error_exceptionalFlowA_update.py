# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0107166.001 - SmartMeter_sendAlertMessage_first_udp_configure_error_exceptionalFlowA_update
# Hints:
# Some parameters should be defined in local.cfg currently,such as ftps_server_ipv4 and etc.

import unicorn
import time
import datetime
import re
import os
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_send_alert_message_normal_flow_update
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.auxiliary.generate_data import dstl_generate_data

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(True)

    def run(test):

        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        send_alert_message_first_udp_configure_error_exceptional_flowA_update(test)

    def cleanup(test):
        pass

def send_alert_message_first_udp_configure_error_exceptional_flowA_update(test):

    global power_save_period, power_save_wakeup
    power_save_period = 52
    power_save_wakeup = 50
    global tamperingAttempt_status, glitch_status, power_loss, ipVersion
    tamperingAttempt_status = False
    glitch_status = False
    power_loss = False
    ipVersion = "4"
    test.log.info('*** send_alert_message_first_udp_configure_error_exceptional_flowA_update begin ***')
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

    test.log.step('NF-04:  Check if really power loss or only a glitch for 9 seconds.')
    time.sleep(9)
    test.dut.dstl_collect_result('NF-04:  Check if really power loss or only a glitch for 9 seconds.', True)

    test.log.step('NF-05:  Wake up the module.')
    test.dut.dstl_collect_result('NF-05:  Wake up the module',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_normal_flow_update.wake_up_module,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-06: disables power saving.')
    test.dut.dstl_collect_result('NF-06: disables power saving.',
                                 smart_meter_init_module_normal_flow.retry(test, disable_power_saving_mode,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-07: Check if only a glitch.')
    glitch_status = False
    test.dut.dstl_collect_result('NF-07: Check if only a glitch.', True)

    test.log.step('Perepare for trigger error')
    test.expect(test.dut.at1.send_and_verify("AT^SISS=0,srvtype,socket", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SISS=0,address,"sockudp://' + test.udp_echo_server_ipv4 + ':' + str(test.udp_echo_server_port_ipv4) + '"', ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT^SISO=0",".*OK|.*0"))

    test.log.step('NF-08: Configure the first UDP socket.--- Trigger error')
    test.log.step('NF-09: Shut down the module via at^smso.')
    test.log.step('NF-10: Wait a security time about 5 seconds.')
    test.log.step('NF-11: Boot up the module via the ignition line and re-initialized module.')
    test.dut.dstl_collect_result('NF-08: Configure the first UDP socket.\n'
                                 'NF-09: Shut down the module via at^smso.\n'
                                 'NF-10: Wait a security time about 5 seconds.\n'
                                 'NF-11: Boot up the module via the ignition line and re-initialized module.',
                                 smart_meter_init_module_normal_flow.retry(test, configure_udp1_socket,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.dut.at1.reconfigure({"rtscts": False})
    test.log.step('NF-12: Repeat step1-8 --- NF-01: Check for listener mode.')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-01: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-01: Check for listener mode', True)

    test.log.step('NF-12: Repeat step1-8 --- NF-02: Check if tampering attempt.')
    tamperingAttempt_status = False
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-02: Check if tampering attempt.', True)

    test.log.step('NF-12: Repeat step1-8 --- NF-03: Send the module to sleep.')
    enable_power_saving_mode(test)
    test.expect(test.dut.at1.send_and_verify("AT\Q 0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-03: Send the module to sleep.',
                                 smart_meter_init_module_normal_flow.retry(test, check_enter_sleep,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-12: Repeat step1-8 --- NF-04:  Check if really power loss or only a glitch for 9 seconds.')
    time.sleep(9)
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-04:  Check if really power loss or only a glitch for 9 seconds.', True)

    test.log.step('NF-12: Repeat step1-8 --- NF-05:  Wake up the module.')
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-05:  Wake up the module',
                                 smart_meter_init_module_normal_flow.retry(test,
                                                                           smart_meter_send_alert_message_normal_flow_update.wake_up_module,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-12: Repeat step1-8 --- NF-06: disables power saving.')
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-06: disables power saving.',
                                 smart_meter_init_module_normal_flow.retry(test, disable_power_saving_mode,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-12: Repeat step1-8 --- NF-07: Check if only a glitch.')
    glitch_status = False
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-07: Check if only a glitch.', True)

    test.log.step('NF-12: Repeat step1-8 --- NF-08: Configure the first UDP socket.')
    test.dut.dstl_collect_result('NF-12: Repeat step1-8 --- NF-08: Configure the first UDP socket.',
                                 smart_meter_init_module_normal_flow.retry(test,
                                                                           configure_udp1_socket,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-13: Open UDP socket and send the alert as UDP packet.')
    test.dut.dstl_collect_result('NF-13: Open UDP socket and send the alert as UDP packet',
                                 smart_meter_init_module_normal_flow.retry(test, open_udp_socket_and_send_data,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-14: Wait for 5 secs for reception.')
    test.sleep(5)
    test.dut.dstl_collect_result('NF-14: Wait for 5 secs for reception.',True)

    test.log.step('NF-15: Close the UDP socket.')
    test.dut.dstl_collect_result('NF-15: Close the UDP socket',smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_normal_flow_update.close_udp_socket,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-16: Check if power loss.')
    power_loss = False
    test.dut.dstl_collect_result('NF-16: Check if power loss.', True)



    test.log.step('NF-17: Configure a second UDP socket.')
    test.dut.dstl_collect_result('NF-17: Configure a second UDP socket.',
                                 smart_meter_init_module_normal_flow.retry(test, configure_udp2_socket,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-18: Open UDP socket and send the alert as UDP packet to a second server.')
    test.dut.dstl_collect_result('NF-18: Open UDP socket and send the alert as UDP packet to a second server.',
                                 smart_meter_init_module_normal_flow.retry(test, open_udp_socket_and_send_data,
                                                                     smart_meter_init_module_normal_flow.AF_A_restart,
                                                                     3))

    test.log.step('NF-19: Wait for 5 secs for reception.')
    test.sleep(5)
    test.dut.dstl_collect_result('NF-19: Wait for 5 secs for reception.', True)

    test.log.step('NF-20: Close the second UDP socket..')
    test.dut.dstl_collect_result('NF-20: Close the second UDP socket.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_normal_flow_update.close_udp_socket,
                                                                     smart_meter_init_module_normal_flow.AF_A_restart,
                                                                     3))

    test.log.step('NF-21: Check for listener mode')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        smart_meter_init_module_normal_flow.close_listener(test)
        test.dut.dstl_collect_result('NF-21: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-21: Check for listener mode', True)

    test.dut.dstl_print_results()
    test.log.info('*** send_alert_message_first_udp_configure_error_exceptional_flowA_update end ***')

    return True

def enable_power_saving_mode(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PwrSave","enabled","'+str(power_save_period)+'","' + str(power_save_wakeup) + '"', ".*OK.*|.*0.*"))
    return result

def disable_power_saving_mode(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/PwrSave","disabled","'+str(power_save_period)+'","' + str(power_save_wakeup) + '"', ".*OK.*|.*0.*"))
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

def configure_udp1_socket(test):
    result = True
#    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=0", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    global connection_setup_dut
    connection_setup_dut = dstl_get_connection_setup_object(test.dut)
    con_id = connection_setup_dut.dstl_get_used_cid()
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,srvtype,socket", ".*0.*|.*OK.*"))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,conid," + str(con_id), ".*0.*|.*OK.*"))
    if ipVersion == "4":
        result = result & test.expect(test.dut.at1.send_and_verify('AT^SISS=0,address,sockudp://'+ str(test.udp_echo_server_ipv4) + ':'+ str(test.udp_echo_server_port_ipv4), ".*0.*|.*OK.*"))
        result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,ipver," + ipVersion, ".*0.*|.*OK.*"))
    elif ipVersion == "6":
        result = result & test.expect(test.dut.at1.send_and_verify(
            'AT^SISS=0,address,sockudp://' + str(test.udp_echo_server_ipv6) + ':' + str(test.udp_echo_server_port_ipv6), ".*0.*|.*OK.*"))
        result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,ipver," + ipVersion, ".*0.*|.*OK.*"))
    test.sleep(2)
    return result

def configure_udp2_socket(test):
    result = True
    global connection_setup_dut
    connection_setup_dut = dstl_get_connection_setup_object(test.dut)
    con_id = connection_setup_dut.dstl_get_used_cid()
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=0", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,srvtype,socket", ".*0.*|.*OK.*"))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,conid," + str(con_id), ".*0.*|.*OK.*"))
    if ipVersion == "4":
        result = result & test.expect(test.dut.at1.send_and_verify('AT^SISS=0,address,sockudp://'+ str(test.udp_echo_server_ipv4) + ':'+ str(test.udp_echo_server_port_ipv4), ".*0.*|.*OK.*"))
        result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,ipver," + ipVersion, ".*0.*|.*OK.*"))
    elif ipVersion == "6":
        result = result & test.expect(test.dut.at1.send_and_verify(
            'AT^SISS=0,address,sockudp://' + str(test.udp_echo_server_ipv6) + ':' + str(test.udp_echo_server_port_ipv6), ".*0.*|.*OK.*"))
        result = result & test.expect(test.dut.at1.send_and_verify("AT^SISS=0,ipver," + ipVersion, ".*0.*|.*OK.*"))
    test.sleep(2)
    return result

def open_udp_socket_and_send_data(test):
    result = True
    connection_setup_dut.dstl_activate_internet_connection()
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISO=0", ".*0.*|.*OK.*", wait_for='.*^SISW: 0,1.*',timeout=10))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISO?", ".*0.*|.*OK.*"))
    data = dstl_generate_data(160)
    test.dut.at1.send_and_verify("AT^SISW=0,160", expect=".*\^SISW:.*", timeout=10)
    test.dut.at1.send(data, end='')
    if test.expect(test.dut.at1.wait_for(".*\^SISR: 0,1.*", 10)) == True:
        result = result & test.expect(test.dut.at1.send_and_verify("AT^SISR=0,160", ".*\^SISR:.*"))
    else:
        result = result & False
    return result


if "__main__" == __name__:
    unicorn.main()

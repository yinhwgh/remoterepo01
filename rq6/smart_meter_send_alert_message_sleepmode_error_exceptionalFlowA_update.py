# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0107164.001 - SmartMeter_sendAlertMessage_sleepmode_error_exceptionalFlowA_update
# Hints:
# Some parameters should be defined in local.cfg currently,such as ftps_server_ipv4 and etc.

import unicorn
import time
import re
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from tests.rq6 import smart_meter_init_module_normal_flow
from tests.rq6 import smart_meter_send_alert_message_normal_flow_update
from dstl.auxiliary.test_support_lib import all_results
from dstl.auxiliary.test_support_lib import dstl_collect_result
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(True)

    def run(test):

        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        send_alert_message_sleepmode_error_exceptional_flowA_update(test)

    def cleanup(test):
        pass

def send_alert_message_sleepmode_error_exceptional_flowA_update(test):

    global power_save_period, power_save_wakeup
    power_save_period = 52
    power_save_wakeup = 50
    global tamperingAttempt_status, glitch_status, power_loss, ipVersion
    tamperingAttempt_status = False
    glitch_status = False
    power_loss = False
    ipVersion = "4"
    test.log.info('*** send_alert_message_sleepmode_error_exceptional_flowA_update begin ***')
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

    test.log.step('NF-03: Send the module to sleep. --- Trigger error')
    test.log.step('NF-04: Shut down the module via at^smso.')
    test.log.step('NF-05: Wait a security time about 5 seconds.')
    test.log.step('NF-06: Boot up the module via the ignition line and re-initialized module.')
    disable_power_saving_mode(test)
    test.expect(test.dut.at1.send_and_verify("AT\Q 0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    test.dut.dstl_collect_result('NF-03: Send the module to sleep.\n'
                                 'NF-04: Shut down the module via at^smso.\n'
                                 'NF-05: Wait a security time about 5 seconds.\n'
                                 'NF-06: Boot up the module via the ignition line and re-initialized module.', smart_meter_init_module_normal_flow.retry(test, check_enter_sleep,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.dut.at1.reconfigure({"rtscts": False})
    test.log.step('NF-07: Repeat step1-3 --- NF-01: Check for listener mode.')
    smart_meter_init_module_normal_flow.set_listener_mode(False)
    if smart_meter_init_module_normal_flow.check_listener_mode(test):
        if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
            return
        else:
            smart_meter_init_module_normal_flow.close_listener(test)
            test.dut.dstl_collect_result('NF-07: Repeat step1-3 --- NF-01: Check for listener mode', False)
    test.dut.dstl_collect_result('NF-07: Repeat step1-3 --- NF-01: Check for listener mode', True)

    test.log.step('NF-07: Repeat step1-3 --- NF-02: Check if tampering attempt.')
    tamperingAttempt_status = False
    test.dut.dstl_collect_result('NF-07: Repeat step1-3 --- NF-02: Check if tampering attempt.', True)

    test.log.step('NF-07: Repeat step1-3 --- NF-03: Send the module to sleep.')
    enable_power_saving_mode(test)
    test.expect(test.dut.at1.send_and_verify("AT\Q 0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    test.dut.dstl_collect_result('NF-07: Repeat step1-3 --- NF-03: Send the module to sleep.', smart_meter_init_module_normal_flow.retry(test, check_enter_sleep,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-08:  Check if really power loss or only a glitch for 9 seconds.')
    time.sleep(9)
    test.dut.dstl_collect_result('NF-08:  Check if really power loss or only a glitch for 9 seconds.', True)

    test.log.step('NF-09:  Wake up the module.')
    test.dut.dstl_collect_result('NF-09:  Wake up the module.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_normal_flow_update.wake_up_module,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-10: disables power saving.')
    test.dut.dstl_collect_result('NF-10: disables power saving.',
                                 smart_meter_init_module_normal_flow.retry(test, disable_power_saving_mode,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))

    test.log.step('NF-11: Check if only a glitch.')
    glitch_status = False
    test.dut.dstl_collect_result('NF-11: Check if only a glitch.',True)

    test.log.step('NF-12: Configure the first UDP socket.')
    test.dut.dstl_collect_result('NF-12: Configure the first UDP socket',
                                 smart_meter_init_module_normal_flow.retry(test, configure_udp1_socket,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

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
    test.log.info('*** send_alert_message_sleepmode_error_exceptional_flowA_update end ***')

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
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=0", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    global connection_setup_dut
    connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
    con_id = connection_setup_dut.dstl_get_used_cid()
    global udp_client
    if ipVersion == "4":
        udp_client = SocketProfile(test.dut, srv_profile_id=0, con_id=con_id, protocol="udp", host=test.udp_echo_server_ipv4, port=test.udp_echo_server_port_ipv4,
                                ip_version=ipVersion)
    elif ipVersion == "6":
        udp_client = SocketProfile(test.dut, srv_profile_id=0, con_id=con_id, protocol="udp", host=test.udp_echo_server_ipv6,
                                   port=test.udp_echo_server_port_ipv6,
                                   ip_version=ipVersion)

    udp_client.dstl_generate_address()
    udp_client.dstl_get_service().dstl_load_profile()
    test.sleep(2)

    return result

def configure_udp2_socket(test):
    result = True
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISC=0", ".*0.*|.*4.*|.*OK.*|.*ERROR.*"))
    global connection_setup_dut
    connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version='IPv4')
    con_id = connection_setup_dut.dstl_get_used_cid()
    global udp_client
    if ipVersion == "4":
        udp_client = SocketProfile(test.dut, srv_profile_id=0, con_id=con_id, protocol="udp", host=test.udp_echo_server_fqdn, port=test.udp_echo_server_port_fqdn,
                                ip_version=ipVersion)
    elif ipVersion == "6":
        udp_client = SocketProfile(test.dut, srv_profile_id=0, con_id=con_id, protocol="udp", host=test.udp_echo_server_fqdn, port=test.udp_echo_server_port_fqdn,
                                ip_version=ipVersion)

    udp_client.dstl_generate_address()
    udp_client.dstl_get_service().dstl_load_profile()
    test.sleep(2)

    return result

def open_udp_socket_and_send_data(test):
    result = True
    connection_setup_dut.dstl_activate_internet_connection()
    udp_client.dstl_get_service().dstl_open_service_profile(expected=".*OK.*|.*ERROR.*")
    result = result & test.expect(udp_client.dstl_get_urc().dstl_is_sisw_urc_appeared(1))
    result = result & test.expect(test.dut.at1.send_and_verify("AT^SISO?", ".*OK.*|.*0.*"))
    udp_client.dstl_get_service().dstl_send_sisw_command_and_data(160)
    if udp_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1", timeout=10) == True:
        udp_client.dstl_get_service().dstl_read_data(160)

    return result

if "__main__" == __name__:
    unicorn.main()

# responsible: shuang.liang@thalesgroup.com
# location: Beijing
# TC0107139.001 - SmartMeter_sendAlertMessage_alternativeFlowA_update
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

class Test(BaseTest):
    def setup(test):
        smart_meter_init_module_normal_flow.set_run_all(False)

    def run(test):

        test.log.step('Preparation: Register network.')
        smart_meter_init_module_normal_flow.uc_init_module(test, 1)
        send_alert_message_alternative_flowA_update(test)

    def cleanup(test):
        pass

def send_alert_message_alternative_flowA_update(test):

    global tamperingAttempt_status, glitch_status, power_loss, ipVersion
    tamperingAttempt_status = False
    glitch_status = False
    power_loss = False
    ipVersion = "4"
    test.log.info('*** send_alert_message_alternative_flowA_update begin ***')
    test.dut.at1.reconfigure({"rtscts": False})

    test.log.step('Preparation for triggering NF-02: Define and open TCP listener service.')
    test.expect(test.dut.at1.send_and_verify("ATV1", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    connection_setup_dut = test.dut.dstl_get_connection_setup_object(ip_public=True)
    #    test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

    socket_listener = SocketProfile(test.dut, "2", connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                    host="listener", localport=65100)
    socket_listener.dstl_generate_address()
    test.expect(socket_listener.dstl_get_service().dstl_load_profile())

    test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
    test.dut.dstl_collect_result('Preparation for triggering NF-02: Define and open TCP listener service.',
                                 test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n")))
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

    test.log.step('NF-04: Check if tampering attempt.')
    tamperingAttempt_status = False
    test.dut.dstl_collect_result('NF-04: Check if tampering attempt.', True)

    test.log.step('NF-05: Send the module to sleep.')
    enable_power_saving_mode(test)
    test.expect(test.dut.at1.send_and_verify("AT\Q 0", ".*OK|.*0"))
    test.expect(test.dut.at1.send_and_verify('AT^SCFG="tcp/withurcs","on"', ".*OK|.*0"))
    test.dut.dstl_collect_result('NF-05: Send the module to sleep.', smart_meter_init_module_normal_flow.retry(test, check_enter_sleep,
                                              smart_meter_init_module_normal_flow.AF_A_restart, 3))

    test.log.step('NF-06:  Check if really power loss or only a glitch for 9 seconds.')
    time.sleep(9)
    test.dut.dstl_collect_result('NF-06:  Check if really power loss or only a glitch for 9 seconds.', True)

    test.log.step('NF-07:  Wake up the module.')
    test.dut.dstl_collect_result('NF-07:  Wake up the module.',
                                 smart_meter_init_module_normal_flow.retry(test, smart_meter_send_alert_message_normal_flow_update.wake_up_module,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))
    test.log.step('NF-08: disables power saving.')
    test.dut.dstl_collect_result('NF-08: disables power saving.',
                                 smart_meter_init_module_normal_flow.retry(test, disable_power_saving_mode,
                                                                           smart_meter_init_module_normal_flow.AF_A_restart,
                                                                           3))
    test.log.step('NF-09: Check if only a glitch.')
    glitch_status = False
    test.dut.dstl_collect_result('NF-09: Check if only a glitch.',True)

    test.log.step('NF-10: Configure the first UDP socket.')
    test.dut.dstl_collect_result('NF-10: Configure the first UDP socket',smart_meter_init_module_normal_flow.retry(test,
                                                        configure_udp1_socket, smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-11: Open UDP socket and send the alert as UDP packet.')
    test.dut.dstl_collect_result('NF-11: Open UDP socket and send the alert as UDP packet',smart_meter_init_module_normal_flow.retry(test,
                                           open_udp_socket_and_send_data, smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-12: Wait for 5 secs for reception.')
    test.sleep(5)
    test.dut.dstl_collect_result('NF-12: Wait for 5 secs for reception.', True)

    test.log.step('NF-13: Close the UDP socket.')
    test.dut.dstl_collect_result('NF-13: Close the UDP socket',smart_meter_init_module_normal_flow.retry(test,
                                                        smart_meter_send_alert_message_normal_flow_update.close_udp_socket,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-14: Check if power loss.')
    power_loss = False
    test.dut.dstl_collect_result('NF-14: Check if power loss.', True)

    test.log.step('NF-15: Configure a second UDP socket.')
    test.dut.dstl_collect_result('NF-15: Configure a second UDP socket.',smart_meter_init_module_normal_flow.retry(test, configure_udp2_socket,
                                                                          smart_meter_init_module_normal_flow.AF_A_restart,3))

    test.log.step('NF-16: Open UDP socket and send the alert as UDP packet to a second server.')
    test.dut.dstl_collect_result('NF-16: Open UDP socket and send the alert as UDP packet to a second server.',
                                 smart_meter_init_module_normal_flow.retry(test, open_udp_socket_and_send_data,
                                                                     smart_meter_init_module_normal_flow.AF_A_restart,
                                                                     3))

    test.log.step('NF-17: Wait for 5 secs for reception.')
    test.sleep(5)
    test.dut.dstl_collect_result('NF-17: Wait for 5 secs for reception.', True)

    test.log.step('NF-18: Close the second UDP socket.')
    test.dut.dstl_collect_result('NF-18: Close the second UDP socket.',
                                 smart_meter_init_module_normal_flow.retry(test,
                                                    smart_meter_send_alert_message_normal_flow_update.close_udp_socket,
                                                                     smart_meter_init_module_normal_flow.AF_A_restart,
                                                                     3))

    test.log.step('NF-19: Check for listener mode')
    if smart_meter_init_module_normal_flow.get_run_all() == True:
        smart_meter_init_module_normal_flow.set_listener_mode(True)
        if smart_meter_init_module_normal_flow.check_listener_mode(test) == True:
            test.dut.dstl_collect_result(
                'NF-19: Check for listener mode during duration test--It should be true and got to UC ProvideDataConnection',
                True)
            return True
    elif smart_meter_init_module_normal_flow.get_run_all() == False:
        if smart_meter_init_module_normal_flow.check_listener_mode(test):
            if smart_meter_init_module_normal_flow.check_dcd_line(test) is True:
                return
            else:
                smart_meter_init_module_normal_flow.close_listener(test)
                test.dut.dstl_collect_result('NF-19: Check for listener mode with DCD checking and closing listener',
                                             True)
        else:
            test.dut.dstl_collect_result(
                'NF-19: Check for listener mode without operation of DCD checking and closing listener', True)

    test.dut.dstl_print_results()
    test.log.info('*** send_alert_message_alternative_flowA_update end ***')
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

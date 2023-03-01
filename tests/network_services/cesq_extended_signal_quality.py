# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0093633.001


import unicorn

from core.basetest import BaseTest

from dstl.network_service import register_to_network
from dstl.auxiliary import restart_module
from dstl.auxiliary.init import dstl_detect
from dstl.security import lock_unlock_sim
from dstl.configuration import network_registration_status
from dstl.configuration import functionality_modes
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service import customization_cesq_test_response
from dstl.call import switch_to_command_mode
from dstl.auxiliary.ip_server.echo_server import EchoServer
import re


class Test(BaseTest):
    '''
    TC0093633.001 -  CesqExtendedSignalQuality
    Check functionality of AT+CESQ command.
    Subscribers: two interfaces of dut
    '''

    def setup(test):
        test.dut.dstl_detect()
        test.port_1 = test.dut.at1
        test.are_two_interfaces_configured()
        # Key is scenario, the first item in value_list is expected cesq response
        # The second item in value_list is expected smoni response
        test.verbose_error_dict = {
            "ERROR_CFUN_0": ["\+CME ERROR: SIM not inserted", "\+CME ERROR: operation not supported"],
            "ERROR_CFUN_4": ["\+CME ERROR: operation not supported", "\+CME ERROR: operation not supported"],
            "ERROR_CFUN_4_no_pin": ["\+CME ERROR: SIM PIN required", "\+CME ERROR: operation not supported"],
            "ERROR_CFUN_1_no_pin": ["\+CME ERROR: SIM PIN required", ",LIMSRV(\s+|,)"],
            "ERROR_CFUN_1_remove_pin": ["\+CME ERROR: SIM not inserted", ",LIMSRV(\s+|,)"]
        }
        test.cesq_test_response = test.dut.dstl_get_customized_cesq_test_response()

    def run(test):
        test.log.info("Step 1. Enable PIN and restart the module.")
        test.expect(test.dut.dstl_lock_sim())
        test.expect(test.dut.dstl_restart())

        test.log.info(
            "Step 2. Set verbose error message format and enable network registration URC on two interfaces (ASC0 and USB).")
        test.expect(test.port_1.send_and_verify(f"AT+CMEE=2", "OK"))
        test.expect(test.dut.dstl_set_common_network_registration_urc(test.port_1))
        test.expect(test.port_2.send_and_verify(f"AT+CMEE=2", "OK"))
        test.expect(test.dut.dstl_set_common_network_registration_urc(test.port_2))

        test.log.info("Step 3. Set cfun to airplane mode.")
        test.expect(test.dut.dstl_set_airplane_mode())

        test.log.info("Step 4.  Send exec smoni comand and test and exec cesq command.")
        test.check_smoni_and_cesq(test.port_2, "ERROR_CFUN_4_no_pin")

        test.log.info("Step 5.  Enter the PIN and repeat step 4.")
        test.expect(test.dut.dstl_enter_pin())
        test.check_smoni_and_cesq(test.port_2, "ERROR_CFUN_4")

        test.log.info("Step 6.  Set cfun to minimum functionality level and repeat step 4.")
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.dstl_set_minimum_functionality_mode())
        test.check_smoni_and_cesq(test.port_2, "ERROR_CFUN_0")

        test.log.info("Step 7.  Set cfun to full functionality mode.")
        test.expect(test.dut.dstl_set_full_functionality_mode())

        test.log.info("Step 8.  Check the PIN is not entered and repeat step 4.")
        test.attempt(test.dut.at1.send_and_verify, "AT+CPIN?", "SIM PIN", wait_for="SIM PIN", timeout=5, retry=3,
                     sleep=1)
        test.check_smoni_and_cesq(test.port_2, "ERROR_CFUN_1_no_pin")

        test.log.info("Step 9.  Remove the SIM and repeat step 4.")
        test.expect(test.dut.dstl_remove_sim())
        test.check_smoni_and_cesq(test.port_2, "ERROR_CFUN_1_remove_pin")

        test.log.info("Step 10. Enable the SIM and enter the PIN.")
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.dstl_enter_pin(wait_till_ready=False))

        test.log.info("Step 11. Repeat step 4.")
        test.check_smoni_and_cesq(test.port_2, "CFUN_1_AFTER_PIN")

        test.log.info("Step 12. Force LTE data transfer (e.g. UDP communication in loop).")
        test.log.info("Step 13. Repeat step 4 during data transfer.")
        if test.two_ports == True:
            test.check_smoni_and_cesq(test.port_2, "UDP_CONNECTION")
        else:
            test.log.error("Skip step 12 & 13, due to test.dut.at2 is not configured.")
        test.log.info("Step 14. Set back settings with at&f.")
        test.expect(test.dut.at1.send_and_verify("AT&F", "OK"))

    def cleanup(test):
        test.dut.dstl_switch_to_command_mode_by_pluses()
        test.expect(test.socket_profile.dstl_get_service().dstl_close_service_profile())
        test.expect(test.dut.dstl_insert_sim())
        test.expect(test.dut.dstl_restart())

    def are_two_interfaces_configured(test):
        test.two_ports = True
        if test.dut.at2 is not None:
            test.port_2 = test.dut.at2
        elif test.dut.at3 is not None:
            test.port_2 = test.dut.at3
        else:
            test.expect(False,
                        msg="Two ports are necessary for testing this case, please check local.cfg. Use only one port to continue part of the tests.")
            test.port_2 = test.dut.at1
            test.two_ports = False

    def check_smoni_and_cesq(test, test_port, status):
        # status: ERROR, ERROR_CFUN0, ERROR_CFUN4_WITH_PIN, ERROR_CFUN4_WITHOUT_PIN
        # +CESQ: 99,99,255,255,0-34,0-97
        cesq_read_response = "\+CESQ: 99,99,255,255,([0-9]|[1-2][0-9]|3[0-4]),([0-9]|[1-8][0-9]|9[0-7])"
        if status == "CFUN_1_AFTER_PIN":
            test.log.info("****** Cell state should be CONN at first then change to NOCONN ******")
            test.log.info("****** CESQ value should be in scope +CESQ: 99,99,255,255,0-34,0-97 ******")
            test.attempt(test.port_2.send_and_verify, "AT^SMONI", ",CONN(,|\s)", retry=10, sleep=1)
            test.expect(test.port_2.send_and_verify("AT+CESQ=?", test.cesq_test_response))
            test.expect(test.port_2.send_and_verify("AT+CESQ", cesq_read_response))
            test.sleep(20)
            test.attempt(test.port_2.send_and_verify, "AT^SMONI", ",NOCONN(,|\s)", retry=10, sleep=5)
            test.expect(test.port_2.send_and_verify("AT+CESQ=?", test.cesq_test_response))
            test.expect(test.port_2.send_and_verify("AT+CESQ", cesq_read_response))
        elif status == "UDP_CONNECTION":
            test.log.info("****** Monitor for 10 times, cell state should be CONN during UDP connection ******")
            test.log.info("****** CESQ value should be in scope +CESQ: 99,99,255,255,0-34,0-97 ******")
            test.socket_profile = test.set_up_udp_transparent_mode()
            for i in range(10):
                test.log.info(f"{i + 1}/10")
                test.expect(test.socket_profile.dstl_get_service().dstl_send_data("check cesq", expected=""))
                test.expect(test.port_2.send_and_verify("AT^SMONI", ",CONN(,|\s)"))
                test.expect(test.port_2.send_and_verify("AT+CESQ=?", test.cesq_test_response))
                test.expect(test.port_2.send_and_verify("AT+CESQ", cesq_read_response))
            test.expect(test.dut.dstl_switch_to_command_mode_by_pluses())
            test.expect(test.socket_profile.dstl_get_service().dstl_close_service_profile())
        elif status in test.verbose_error_dict:
            cesq_response, smoni_response = test.verbose_error_dict[status]
            test.log.info(
                f"****** When module in state {status}, SMONI response should be {smoni_response}, CESQ response should be {cesq_response} ******")
            correct_response = test.port_2.send_and_verify("AT^SMONI", smoni_response)
            if not correct_response:
                test.attempt(test.port_2.send_and_verify, "AT^SMONI", smoni_response, retry=5, sleep=5)
            else:
                test.expect(correct_response)
            test.expect(test.port_2.send_and_verify("AT+CESQ=?", cesq_response))
            test.expect(test.port_2.send_and_verify("AT+CESQ", cesq_response))
        else:
            test.expect(False, msg=f"Undefined status value {status}")

    def set_up_udp_transparent_mode(test):
        test.echo_server = EchoServer("IPv4", "UDP")
        test.expect(test.dut.dstl_register_to_network())
        socket_profile_id = 1
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        used_cid = connection_setup_dut.dstl_get_used_cid()
        test.socket_profile = SocketProfile(test.dut, socket_profile_id, used_cid, protocol="udp", etx_char=26)
        test.socket_profile.dstl_set_parameters_from_ip_server(test.echo_server)
        test.socket_profile.dstl_generate_address()
        test.expect(test.socket_profile.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_profile.dstl_get_service().dstl_open_service_profile())
        connection_is_ready = test.socket_profile.dstl_get_service().dstl_enter_transparent_mode()
        if connection_is_ready:
            test.log.info("****** UDP connection is established successfully  ******")
        else:
            test.expect(False, msg="Fail to establish UDP connection")
        return test.socket_profile


if __name__ == '__main__':
    unicorn.main()

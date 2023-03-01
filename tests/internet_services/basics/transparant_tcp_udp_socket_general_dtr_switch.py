# responsible: lei.chen@thalesgroup.com
# location: Dalian
# TC0093528.001, TC0093528.003
# Parameters that should be configured to local.cfg
# udp_echo_server_ipv4 =78.47.86.194
# udp_echo_server_port_ipv4 = 7

import unicorn
from core.basetest import BaseTest
from dstl.network_service import register_to_network
from dstl.auxiliary import init
from dstl.auxiliary import restart_module
from dstl.call import switch_to_command_mode
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary import check_urc
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
import re


class Test(BaseTest):
    """
    TC0093528.001, TC0093528.003 - TransparentTcpUdpSocketGeneralDtrSwitch
    Check proper behaviour of the AT&D settings for DTR toggle on serial (if product support it) and USB interface.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.expect(test.dut.dstl_register_to_network())
        test.udp_socket_profile_id = 1
        test.tcp_socket_profile_id = 2
        test.dut.at1.send_and_verify("AT^SCFG?")
        scfg_response = test.dut.at1.last_response.lower()
        if "gpio/mode/dcd0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dcd0\",\"std\"")
        if "gpio/mode/dsr0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dsr0\",\"std\"")
        if "gpio/mode/dtr0" in scfg_response:
            test.dut.at1.send_and_verify("AT^SCFG=\"gpio/mode/dtr0\",\"std\"")

    def run(test):
        commands_to_test = {
            "AT&D0": "ME ignores status of DTR line",
            "AT&D1": "ME should switch to command mode",
            "AT&D2": "ME should switch to command mode"
        }
        ext_char = 26

        test.log.info("Step 1. Setup Internet Connection Profile")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.log.info("Step 2. Setup two Internet Services - one Transparent UDP Client and one Transparent TCP client")
        test.log.info("Step 3. Activate Internet Connection")
        test.log.info("Step 4. Open both services and wait for proper URC")
        udp_client, test.udp_service = test.setup_socket_connection(protocol="udp")
        tcp_client, test.tcp_service = test.setup_socket_connection(protocol="tcp")

        for command, description in commands_to_test.items():
            test.log.step(f"******** {command} - START ********")
            d_value = command.strip("AT&D")
            test.expect(test.dut.at1.send_and_verify(command, "OK"))
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(d_value)))
            for protocol in ('udp', 'tcp'):
                test.log.step(f"******** {command}: {protocol} - START ********")
                client = eval(f'{protocol}_client')
                service = eval(f'test.{protocol}_service')

                test.log.info(f"Step 5. Switch Transparent {protocol} client to Transparent mode")
                test.enter_transparent_mode(service, protocol)

                test.log.info("Step 6. Toggle DTR line to escape from transparent mode")
                test.toggle_dtr()

                if d_value == '0':
                    test.expect(not test.dut.at1.wait_for('OK', timeout=15))
                    test.log.info("Step 7. Fall back to command mode by sending ETX char")
                    test.dut.dstl_switch_to_command_mode_by_etxchar(ext_char)
                else:
                    command_mode = test.dut.at1.wait_for('OK', timeout=15)
                    if not command_mode:
                        test.log.error(f"{command}: toggle DTR line, module does not switch to command mode.")
                        test.dut.dstl_switch_to_command_mode_by_etxchar(ext_char)
                    else:
                        test.log.info(f"{command}: toggle DTR line, module is switched to command mode.")
                        test.expect(service.dstl_check_if_module_in_command_mode())

                test.log.info("Step 8. Check the Service and Socket state")
                test.expect(client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
                test.expect(client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
                test.log.step(f"******** {command}: {protocol} - END ********")
            test.log.step(f"******** {command} - END ********")

    def setup_socket_connection(test, protocol="tcp", ext_char=26):
        test.log.h3("****** Setting up socket connectin for {protocol} *********")
        profile_id = eval(f"test.{protocol}_socket_profile_id")
        test.dut.at1.send_and_verify(f"AT^SISC={profile_id}", "OK|ERROR")
        client = SocketProfile(test.dut, profile_id, test.connection_setup_dut.dstl_get_used_cid(), protocol=protocol,
                               etx_char=ext_char,
                               host=test.udp_echo_server_ipv4, port=test.tcp_echo_server_port_ipv4)
        client.dstl_generate_address()
        socket_service = client.dstl_get_service()
        test.expect(socket_service.dstl_load_profile())

        socket_service.dstl_open_service_profile()
        is_connected = test.dut.dstl_check_urc(f'SISW: {profile_id},1')
        if not is_connected:
            test.log.error("Failed to establish socket connection.")
            test.expect(client.dstl_get_service().dstl_close_service_profile())
            test.sleep(5)
        return client, socket_service

    def enter_transparent_mode(test, service, protocol="tcp"):
        test.log.info("******** Entering transparent mode ********")
        profile_id = eval(f"test.{protocol}_socket_profile_id")
        is_connected = service.dstl_enter_transparent_mode(profile_id)
        if not is_connected:
            test.log.error("Failed to enter transparent mode.")
            test.expect(service.dstl_close_service_profile())
            test.sleep(5)
        return is_connected

    def toggle_dtr(test):
        test.log.info("Toggling DTR ON->OFF")
        test.dut.at1.connection.setDTR(True)
        test.dut.at1.connection.setDTR(False)
        test.dut.at1.connection.setDTR(True)

    def cleanup(test):
        test.dut.dstl_switch_to_command_mode_by_pluses()
        test.udp_service.dstl_close_service_profile()
        test.tcp_service.dstl_close_service_profile()
        test.expect(test.dut.at1.send_and_verify("AT&D0", "OK"))


if "__main__" == __name__:
    unicorn.main()

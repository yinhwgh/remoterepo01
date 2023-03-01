# responsible: lei.chen@thalesgroup.com, renata.bryla@globallogic.com
# location: Dalian, Wroclaw
# TC0093528.001, TC0093528.003
# Parameters that should be configured to local.cfg
# udp_echo_server_ipv4 = 78.47.86.194
# udp_echo_server_port_ipv4 = 7

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.check_urc import dstl_check_urc
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar, \
    dstl_switch_to_command_mode_by_pluses, dstl_switch_to_command_mode_by_dtr
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState


class Test(BaseTest):
    """
    TC0093528.001, TC0093528.003 - TransparentTcpUdpSocketGeneralDtrSwitch
    Check proper behaviour of the AT&D settings for DTR toggle on serial (if product support it) and USB interface.
    """

    dicts_of_step_descriptions = [{"command": "AT&D0", "desc": "ME ignores status of DTR line",
                                   "step_switch": "5", "step_toggle": "6", "step_check": "8",
                                   "step_repeat": "9", "steps_to_repeat": "5-8"},
                                  {"command": "AT&D2", "desc": "ME should switch to command mode",
                                   "step_switch": "11", "step_toggle": "12", "step_check": "13",
                                   "step_repeat": "14", "steps_to_repeat": "11-13"},
                                  {"command": "AT&D1", "desc": "ME should switch to command mode",
                                   "step_switch": "18", "step_toggle": "19", "step_check": "20",
                                   "step_repeat": "21", "steps_to_repeat": "18-20"}]
    etx_char = 26
    udp_socket_profile_id = 1
    tcp_socket_profile_id = 2

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_get_bootloader(test.dut)
        test.dut.at1.send_and_verify("AT^SCFG?", ".*OK.*")
        test.expect(test.dut.dstl_register_to_network())
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.udp_server = EchoServer("IPv4", "UDP")
        test.tcp_server = EchoServer("IPv4", "TCP")
        try:
            test.dut.devboard.send_and_verify("mc:asc0=ext", "OK")
        except AttributeError:
            test.log.warn("dut_devboard is not defined in configuration file")

    def run(test):
        test.log.step("Step 1. Setup Internet Connection Profile")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_internet_connection_profile())

        test.log.step("Step 2. Setup two Internet Services - one Transparent UDP Client and one Transparent TCP client")
        test.udp_client = test.setup_socket_connection("udp", test.udp_socket_profile_id, test.udp_server)
        test.tcp_client = test.setup_socket_connection("tcp", test.tcp_socket_profile_id, test.tcp_server)

        test.log.step("Step 3. Activate Internet Connection")
        test.expect(test.connection_setup.dstl_activate_internet_connection())

        test.log.step("Step 4. Open both services and wait for proper URC")
        test.open_service(test.udp_client, test.udp_socket_profile_id)
        test.open_service(test.tcp_client, test.tcp_socket_profile_id)

        for item in test.dicts_of_step_descriptions:
            test.log.info("******** {} - START ********".format(item["command"]))
            test.log.info("******** {} ********".format(item["desc"]))
            if item["command"] == "AT&D2":
                test.log.step("Step 10. Set AT&D to 2")
            d_value = item["command"].strip("AT&D")
            test.expect(test.dut.at1.send_and_verify(item["command"], ".*OK.*"))
            test.expect(test.dut.at1.send_and_verify("AT&V", ".*&D{}.*".format(d_value)))

            for protocol in ("udp", "tcp"):
                test.log.info("******** {}: {} - START ********".format(item["command"], protocol))
                client = eval("test.{}_client".format(protocol))

                test.log.step(
                    "Step {}. Switch Transparent {} client to Transparent mode".format(item["step_switch"], protocol))
                test.enter_transparent_mode(client)

                test.log.step("Step {}. Toggle DTR line to escape from transparent mode".format(item["step_toggle"]))
                if d_value == "0":
                    test.expect(not dstl_switch_to_command_mode_by_dtr(test.dut))
                    test.log.step("Step 7. Fall back to command mode by sending ETX char")
                    dstl_switch_to_command_mode_by_etxchar(test.dut, test.etx_char)
                else:
                    if not (dstl_switch_to_command_mode_by_dtr(test.dut)):
                        test.expect(False, msg="problem with leaving transparent mode by DTR")
                        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

                test.log.step("Step {}. Check the Service and Socket state".format(item["step_check"]))
                test.expect(client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
                test.expect(client.dstl_get_parser().dstl_get_socket_state() == SocketState.CLIENT.value)
                test.log.info("******** {}: {} - END ********".format(item["command"], protocol))

                if protocol == "udp":
                    test.log.step("Step {}. Repeat step {} for Transparent TCP service".format(item["step_repeat"],
                                                                                               item["steps_to_repeat"]))
            test.log.info("******** {} - END ********".format(item["command"]))

            if item["command"] == "AT&D2":
                test.log.step("Step 15. Close the Services")
                test.expect(test.udp_client.dstl_get_service().dstl_close_service_profile())
                test.expect(test.tcp_client.dstl_get_service().dstl_close_service_profile())

                test.log.step("Step 16. Open the services")
                test.open_service(test.udp_client, test.udp_socket_profile_id)
                test.open_service(test.tcp_client, test.tcp_socket_profile_id)

                test.log.step("Step 17. Set AT&D to 1")

    def cleanup(test):
        try:
            if not test.udp_server.dstl_server_close_port() or not test.tcp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        dstl_switch_to_command_mode_by_pluses(test.dut)
        test.log.step("Step 22. Close the services")
        test.expect(test.udp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.tcp_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.dut.at1.send_and_verify("AT&D2", ".*OK.*"))

    def setup_socket_connection(test, protocol, profile_id, server):
        test.log.info("****** Setting up socket connection for {} *********".format(protocol))
        client = SocketProfile(test.dut, profile_id, test.connection_setup.dstl_get_used_cid(), protocol=protocol,
                               host=server.dstl_get_server_ip_address(), port=server.dstl_get_server_port(),
                               etx_char=test.etx_char)
        client.dstl_generate_address()
        test.expect(client.dstl_get_service().dstl_load_profile())
        return client

    def open_service(test, client, profile_id):
        test.log.info("******** Open Service ********")
        test.expect(client.dstl_get_service().dstl_open_service_profile())
        if not test.expect(dstl_check_urc(test.dut, 'SISW: {},1'.format(profile_id))):
            test.expect(client.dstl_get_service().dstl_close_service_profile())
            test.sleep(5)

    def enter_transparent_mode(test, client):
        test.log.info("******** Entering transparent mode ********")
        if not test.expect(client.dstl_get_service().dstl_enter_transparent_mode()):
            test.expect(client.dstl_close_service_profile())
            test.sleep(5)


if "__main__" == __name__:
    unicorn.main()
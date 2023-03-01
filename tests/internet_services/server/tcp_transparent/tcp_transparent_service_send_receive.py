# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0092908.001, TC0092908.004

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo
from dstl.configuration.configure_dtr_line_mode import dstl_set_dtr_line_mode
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr, \
    dstl_switch_to_command_mode_by_pluses
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """Intention:
    Verify basic functionality of the Transparent TCP Listener

    description:
    1) Set AT&D to 2
    2) Attach modules to PS
    3) Depends on product:
     - Setup Internet Connection Profile (GPRS)
     - Define PDP context
    4) Setup Internet Service Profile
    DUT – Transparent TCP Listener
    Remote – Transparent TCP Client
    5) Depends on product:
    - Activate PDP context
    6) Open Service:
    6.1) First open Service on DUT side
    6.2) Open the Service on remote side
    7) DUT: wait for ^SIS URC and accept incoming connection and check service state.
    8) Switch both modules to Data Mode
    9) Send 3kb from DUT to Remote and vice versa
    10) Fall-back to Command via DTR
    11) Check service and Socket state. Check RX and TX counters on both modules
    12) Close all services
    13) If product supports AT&D1, set AT&D to 1 and repeat step 6 - 12"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2"))
        try:
            dstl_switch_off_at_echo(test.dut, serial_ifc=0)
        except AttributeError:
            test.log.warn("dut_devboard is not defined in configuration file")

    def run(test):
        test.log.step("1) Set AT&D to 2")
        test.expect(dstl_set_dtr_line_mode(test.dut, "2"))

        test.log.step("2) Attach modules to PS")
        test.log.info("Will be done in next step")

        test.log.step("3) Depends on product:\r\n"
                      "- Setup Internet Connection Profile (GPRS)\r\n"
                      "- Define PDP context")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2")
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("4) Setup Internet Service Profile\r\n"
                      "DUT – Transparent TCP Listener\r\n"
                      "Remote – Transparent TCP Client")
        test.socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(),
                                        protocol="tcp", host="listener", localport=8888,
                                        etx_char=26, autoconnect=0, connect_timeout="90")
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip = test.socket_dut.dstl_get_parser()\
            .dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.socket_remote = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(),
                                           protocol="tcp", host=dut_ip[0], port=dut_ip[1],
                                           etx_char=26, device_interface="at2")
        test.socket_remote.dstl_generate_address()
        test.expect(test.socket_remote.dstl_get_service().dstl_load_profile())

        test.log.step("5) Depends on product:"
                      "- Activate PDP context")
        test.log.info("Done in step 3")

        for atd in ["at&d2", "at&d1"]:
            test.log.step("6) Open Service:")
            test.log.step("6.1) First open Service on DUT side")
            if atd == "at&d1":
                test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            else:
                test.log.info("Listener opened in step 4")

            test.log.step("6.2) Open the Service on remote side")
            test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())

            test.log.step("7) DUT: wait for ^SIS URC and accept incoming connection and "
                          "check service state.")
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3"))
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.CONNECTED.value)
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() ==
                        SocketState.SERVER.value)

            test.log.step("8) Switch both modules to Data Mode")
            test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
            test.expect(test.socket_remote.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("9) Send 3kb from DUT to Remote and vice versa")
            data_length = 1500
            packet_amount = 2
            for loop in range(packet_amount):
                test.socket_remote.dstl_get_service().dstl_send_data(
                    dstl_generate_data(data_length), expected="")
                test.socket_dut.dstl_get_service().dstl_send_data(
                    dstl_generate_data(data_length), expected="")
            test.sleep(5)

            test.log.step("10) Fall-back to Command via DTR")
            test.expect(dstl_switch_to_command_mode_by_dtr(test.r1, device_interface="at2"))
            if not test.expect(
                    test.socket_remote.dstl_get_service().dstl_check_if_module_in_command_mode()):
                dstl_switch_to_command_mode_by_pluses(test.r1, device_interface="at2")

            test.expect(dstl_switch_to_command_mode_by_dtr(test.dut))
            if not test.expect(
                    test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode()):
                dstl_switch_to_command_mode_by_pluses(test.dut)

            test.expect(test.socket_dut.dstl_get_service().dstl_check_if_module_in_command_mode())

            test.log.step("11) Check service and Socket state. Check RX and TX counters "
                          "on both modules")
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() ==
                        ServiceState.CONNECTED.value)
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_socket_state() ==
                        SocketState.SERVER.value)

            test.expect(test.socket_remote.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                        data_length*packet_amount)
            test.expect(test.socket_remote.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                        data_length * packet_amount)

            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                        data_length*packet_amount)
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                        data_length*packet_amount)

            test.log.step("12) Close all services")
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())

            if atd == "at&d2":
                test.log.step("13) If product supports AT&D1, set AT&D to 1 and repeat step 6 - 12")
                test.expect(dstl_set_dtr_line_mode(test.dut, "1"))

    def cleanup(test):
        dstl_set_scfg_urc_dst_ifc(test.r1)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()

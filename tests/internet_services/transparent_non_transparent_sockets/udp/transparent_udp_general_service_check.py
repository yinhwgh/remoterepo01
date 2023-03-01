#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0093525.001, TC0093525.002

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.devboard.devboard import dstl_switch_off_at_echo
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.internet_service.parser.internet_service_parser import ServiceState, SocketState, Command
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_dtr, \
    dstl_switch_to_command_mode_by_pluses,dstl_switch_to_command_mode_by_etxchar
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    TC intention: Intention of this TC is to check Service state, Socket state, RX and TX counters
    before/after upload/download data
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.dut.at1.send_and_verify("AT&D2")
        dstl_enter_pin(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.udp_server = EchoServer("IPV4", "UDP")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

        try:
            dstl_switch_off_at_echo(test.dut, serial_ifc=0)
        except AttributeError:
            test.log.warn("dut_devboard is not defined in configuration file")

    def run(test):
        escape_methods = ["DTR toggle", "ETX", "+++"]

        test.log.step("1) Setup Internet Connection (if required)")
        test.connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2) Setup Internet Service Profile for Transparent UDP client (ETX=26)")
        test.socket = SocketProfile(test.dut, "0", test.connection_setup.dstl_get_used_cid(),
                                    protocol="udp",
                                    host=test.udp_server.dstl_get_server_ip_address(),
                                    port=test.udp_server.dstl_get_server_port(), etx_char="26")
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        for escape_method in escape_methods:
            test.log.step("3) Open the Service")
            test.expect(test.socket.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("4) Check Service and Socket state and compare AT^SISI with AT^SISO "
                          "(one line answer)")
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISI_WRITE) == ServiceState.UP.value)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)

            test.expect(test.socket.dstl_get_parser().dstl_get_socket_state(
                at_command=Command.SISO_WRITE) == SocketState.CLIENT.value)

            test.log.step("5) Switch to Transparent mode")
            test.expect(test.socket.dstl_get_service().dstl_enter_transparent_mode())

            test.log.step("6) Send some data (23552B)")
            data_packet_size = 736
            packets_amount = 32
            data = dstl_generate_data(data_packet_size)
            for data_packet in range(packets_amount):
                test.socket.dstl_get_service().dstl_send_data(data, data)

            data_amount = data_packet_size * packets_amount

            test.log.step("7) Receive data (23552B)")
            test.log.info("executed in previous step")

            test.log.step("8) Fall back to command mode by {}".format(escape_method))
            test.sleep(10) #sleep so all data can be transmitted
            if escape_method == "DTR toggle":
                if not (dstl_switch_to_command_mode_by_dtr(test.dut)):
                    test.expect(False, msg="problem with leaving transparent mode")
                    test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

            elif escape_method == "ETX":
                if not (dstl_switch_to_command_mode_by_etxchar(test.dut, 26)):
                    test.expect(False, msg="problem with leaving transparent mode")
                    test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
            else:
                if not (dstl_switch_to_command_mode_by_pluses(test.dut)):
                    test.expect(False, msg="problem with leaving transparent mode")
                    test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

            test.expect(test.socket.dstl_get_service().dstl_check_if_module_in_command_mode(),
                        critical=True)

            test.log.step("9) Check Service, Socket state and RX, TX counters - compare AT^SISI "
                          "with AT^SISO (one line answer), check assigned IP addresses "
                          "(remote and lo-cal), ports")

            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "rx", at_command=Command.SISO_WRITE) >= data_amount * 0.9)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "tx", at_command=Command.SISO_WRITE) == data_amount)

            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "rx", at_command=Command.SISI_WRITE) >= data_amount * 0.9)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "tx", at_command=Command.SISI_WRITE) == data_amount)

            test.expect(test.socket.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISI_WRITE) == ServiceState.UP.value)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.UP.value)

            test.expect(test.socket.dstl_get_parser().dstl_get_socket_state(
                at_command=Command.SISO_WRITE) == SocketState.CLIENT.value)

            test.expect(test.connection_setup.dstl_get_pdp_address(test.connection_setup.
                                                                   dstl_get_used_cid())[0] in
                        test.socket.dstl_get_parser().
                        dstl_get_service_local_address_and_port('IPv4'))

            test.expect(test.socket.dstl_get_parser().
                        dstl_get_service_remote_address_and_port('IPv4')[0] in
                        test.socket._model.address)

            test.log.step("10) Close the service (AT^SISC)")
            test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

            test.log.step("11) Check Service, Socket state, assigned IP addresses "
                          "(remote and lo-cal), ports as well as RX, TX counters - compare AT^SISI "
                          "with AT^SISO (one line answer).")
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "rx", at_command=Command.SISO_WRITE) == 0)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "tx", at_command=Command.SISO_WRITE) == 0)

            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "rx", at_command=Command.SISI_WRITE) == 0)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_data_counter(
                "tx", at_command=Command.SISI_WRITE) == 0)

            test.expect(test.socket.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISI_WRITE) == ServiceState.ALLOCATED.value)
            test.expect(test.socket.dstl_get_parser().dstl_get_service_state(
                at_command=Command.SISO_WRITE) == ServiceState.ALLOCATED.value)

            test.expect(test.socket.dstl_get_parser().dstl_get_socket_state(
                at_command=Command.SISO_WRITE) == SocketState.NOT_ASSIGNED.value)

            test.expect("0.0.0.0:0" in test.socket.dstl_get_parser().
                        dstl_get_service_local_address_and_port('IPv4'))

            test.expect("0.0.0.0:0" in test.socket.dstl_get_parser().
                        dstl_get_service_remote_address_and_port('IPv4'))

            if escape_method == "DTR toggle":
                test.log.step("12) Repeat Steps 3-11, this time use ETX character to switch in to "
                              "command mode")

            if escape_method == "ETX":
                test.log.step("13) Repeat steps 3-11, this time use Hayes escape sequence (+++) to "
                              "switch in to command mode")


    def cleanup(test):
        try:
            if not test.udp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

        if not (test.socket.dstl_get_service().dstl_check_if_module_in_command_mode()):
            test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))

        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()

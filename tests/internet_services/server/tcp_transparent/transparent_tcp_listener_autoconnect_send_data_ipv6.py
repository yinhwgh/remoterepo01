# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0093721.001, TC0093721.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """This test checks beahaviour of module during transparent connection and functionally
    of the "autoconnect" parameter using IPv6 address. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        test.echo_server = EchoServer('IPv6', 'TCP', extended=True)

    def run(test):
        test.log.h2("Executing test script for: TransparentTCPListenerAutoconnectSendData_IPv6")
        port = test.echo_server.dstl_get_server_port()

        test.log.step("1) Depends on product: \n - Set Connection Profile (GPRS) "
                      "\n - Define PDP Context")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version='IPv6',
                                                                     ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_internet_connection_profile())

        test.log.step("2) Set service profile: TCP transparent listener on DUT")
        socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(),
                                   protocol="tcp", host="listener", localport=port, etx_char=26,
                                   alphabet=1, ip_version='IPv6')
        socket_dut.dstl_generate_address()
        test.expect(socket_dut.dstl_get_service().dstl_load_profile())
        test.socket_dut = socket_dut

        test.log.step("3) Depends on product: \n - Activate PDP Context.")
        test.expect(test.connection_setup_dut.dstl_activate_internet_connection())

        test.log.step("4) Open TCP transparent listener.")
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = socket_dut.dstl_get_parser()\
            .dstl_get_service_local_address_and_port(ip_version='IPv6')
        dut_ip_address = dut_ip_address_and_port[:dut_ip_address_and_port.rindex(':')]

        test.log.step("5) Wait for TCP client request and accept on listener side.")
        test.echo_server.dstl_run_ssh_nc_process(dut_ip_address, port)
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("6) Switch to Transparent mode.")
        test.expect(socket_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("7) Send 50 x 100 bytes from listener to client and from client to listener.")
        block_size = 100
        amount_of_blocks = 50
        data = dstl_generate_data(block_size)
        test.expect(socket_dut.dstl_get_service().dstl_send_data(data, expected="",
                                                                 repetitions=amount_of_blocks))
        for repetition in range(amount_of_blocks):
            test.echo_server.dstl_send_data_from_ssh_server(data)
        test.sleep(5)

        test.log.step("8) Exit from transparent mode.")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

        test.log.step("9) Check service information.")
        parser = socket_dut.dstl_get_parser()
        test.expect(parser.dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(parser.dstl_get_service_data_counter("tx") == amount_of_blocks * block_size)
        test.expect(parser.dstl_get_service_data_counter("rx") == amount_of_blocks * block_size)
        test.expect(len(test.echo_server.dstl_read_data_on_ssh_server()) == amount_of_blocks * block_size)

        test.log.step("10) Close services.")
        test.expect(socket_dut.dstl_get_service().dstl_close_service_profile())
        test.echo_server.dstl_stop_ssh_nc_process()

        test.log.step('11) On DUT change "autoconnect" to enable')
        socket_dut.dstl_set_autoconnect("1")
        socket_dut.dstl_generate_address()
        test.expect(socket_dut.dstl_get_service().dstl_write_address())

        test.log.step("12) Open services - firstly open listener then client")
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.echo_server.dstl_run_ssh_nc_process(dut_ip_address, port)
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "1"))
        test.expect(socket_dut.dstl_get_service().dstl_enter_transparent_mode(send_command=False))

        test.log.step("13) Send 50 x 100 bytes from DUT to Remote and from Remote to DUT")
        test.expect(socket_dut.dstl_get_service().dstl_send_data(data, expected="",
                                                                 repetitions=amount_of_blocks))
        for repetition in range(amount_of_blocks):
            test.echo_server.dstl_send_data_from_ssh_server(data)
        test.sleep(5)

        test.log.step("14) Exit from transparent mode")
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

        test.log.step("15) Check service information")
        test.expect(parser.dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(parser.dstl_get_service_data_counter("tx") == amount_of_blocks * block_size)
        test.expect(parser.dstl_get_service_data_counter("rx") == amount_of_blocks * block_size)
        test.expect(len(test.echo_server.dstl_read_data_on_ssh_server()) == amount_of_blocks * block_size)

        test.log.step("16) Close services")
        test.expect(socket_dut.dstl_get_service().dstl_close_service_profile())
        test.echo_server.dstl_stop_ssh_nc_process()

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.echo_server.dstl_stop_ssh_nc_process()
        except AttributeError:
            test.log.error("Problem with server object.")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())


if "__main__" == __name__:
    unicorn.main()

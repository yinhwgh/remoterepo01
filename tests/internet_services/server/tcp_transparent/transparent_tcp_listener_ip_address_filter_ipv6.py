# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0093723.001, TC0093723.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.packet_domain.select_printing_ip_address_format import dstl_select_printing_ip_address_format


class Test(BaseTest):
    """Check the functionality of "addrfilter" parameter.
    Check proper module behavior with IPv6 protocol stack. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_select_printing_ip_address_format(test.dut, '1')
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.echo_server = EchoServer('IPv6', 'TCP', extended=True)

    def run(test):
        test.log.h2("Executing test script for: TransparentTCPListenerIPAddressFilter_IPv6")

        test.log.step("1) Depends on product: \n - Set Connection Profile. \n "
                      "- Set and activate PDP Context Profile.")
        conn_setup = dstl_get_connection_setup_object(test.dut, ip_version='IPv6',
                                                           ip_public=True)
        test.expect(conn_setup.dstl_load_and_activate_internet_connection_profile())
        test.cid = conn_setup.dstl_get_used_cid()

        test.port = test.echo_server.dstl_get_server_port()
        test.client_ip_address = test.echo_server.dstl_get_server_ip_address()
        dummy_addresses = ['2a00:f22:ab33:0:31b:c682:b7:821f', '2a00:a47:0:ff54:60b8:e765:e7f0:2c',
                           '2001:e234:cf86:0:45b1:c223:7654:551b']

        test.log.step("a) No address filter parameter")
        execute_steps_2_to_8(test, 'a', "", True)

        test.log.step('b) Set IP address of client as "addrfilter"')
        execute_steps_2_to_8(test, 'b', test.client_ip_address, True)

        test.log.step('c) Set IP address of client as "addrfilter", changing last octet to "*"')
        modified_address = (test.client_ip_address[:test.client_ip_address.rindex(':')+1])+'*'
        execute_steps_2_to_8(test, 'c', modified_address, True)

        test.log.step('d) Set three parameters "addrfilter", '
                      'none of which shall allow Remote to connect')
        execute_steps_2_to_8(test, 'd', "{},{},{}".format(dummy_addresses[0], dummy_addresses[1],
                                                          dummy_addresses[2]), False)

        test.log.step('e) Set more than 3 addresses in "addrfilter", '
                      'put client address as 4th in "addrfilter"')
        execute_steps_2_to_8(test, 'e', "{},{},{},{}".format(dummy_addresses[0],
                                                             dummy_addresses[1],
                                                             dummy_addresses[2],
                                                             test.client_ip_address), False)

        test.log.step('f) Set more than 3 addresses in "addrfilter", '
                      'put client address as 3th in "addrfilter"')
        execute_steps_2_to_8(test, 'f', "{},{},{},{}".format(dummy_addresses[0],
                                                             dummy_addresses[1],
                                                             test.client_ip_address,
                                                             dummy_addresses[2]), True)

    def cleanup(test):
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
            test.echo_server.dstl_stop_ssh_nc_process()
        except AttributeError:
            test.log.error("Problem with server object.")
        test.expect(dstl_reset_internet_service_profiles(test.dut, profile_id='0',
                                                         force_reset=True))


def execute_steps_2_to_8(test, scenario, address_filter, should_connect):
    test.log.step("2{}) Set and open TCP Transparent Listener Service Profile on DUT, "
                  "\nset Address Filtering with parameters described below "
                  "(a, b, c, d, e, f).".format(scenario))
    if scenario == 'a':
        test.socket_dut = SocketProfile(test.dut, 0, test.cid, protocol="tcp", host="listener",
                                        localport=test.port, etx_char=26, alphabet=1,
                                        ip_version='IPv6')
    test.socket_dut.dstl_set_addr_filter(address_filter.replace('[', '').replace(']', ''))
    test.socket_dut.dstl_generate_address()
    test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
    test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
    if scenario == 'a':
        test.dut_ip_address = get_ip_address(test, test.socket_dut)

    test.log.step("3{}) Send request from TCP client.".format(scenario))
    test.echo_server.dstl_run_ssh_nc_process(test.dut_ip_address, test.port)

    if should_connect:
        test.log.step("4{}) Establish transparent connection.".format(scenario))
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("5{}) Send 10 x 100 bytes from server to client "
                      "and the same amount from client to server.".format(scenario))
        block_size = 100
        amount_of_blocks = 10
        data = dstl_generate_data(block_size)
        test.expect(test.socket_dut.dstl_get_service().dstl_send_data(data, expected="",
                                                        repetitions=amount_of_blocks))
        for repetition in range(amount_of_blocks):
            test.echo_server.dstl_send_data_from_ssh_server(data)
        test.sleep(5)

        test.log.step("6{}) Exit from transparent mode.".format(scenario))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))

        test.log.step("7{}) Check service information and amount of transferred data."
                      .format(scenario))
        parser = test.socket_dut.dstl_get_parser()
        test.dut.at1.read()
        test.expect(parser.dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(parser.dstl_get_service_data_counter("tx") == amount_of_blocks * block_size)
        test.expect(parser.dstl_get_service_data_counter("rx") == amount_of_blocks * block_size)
        test.expect(len(test.echo_server.dstl_read_data_on_ssh_server())
                    == amount_of_blocks * block_size)
    else:
        test.log.step("4{}) Establish transparent connection.".format(scenario))
        test.expect(not test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.log.h2("Steps 5-7 will be skipped for scenario: '{}'".format(scenario))

    test.log.step("8{}) Close services.".format(scenario))
    test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
    test.echo_server.dstl_stop_ssh_nc_process()

    test.log.step("9) Repeat steps from 2-8 changing Address Filter parameter.")


def get_ip_address(test, profile):
    ip_address_and_port = profile.dstl_get_parser()\
        .dstl_get_service_local_address_and_port(ip_version='IPv6')
    return ip_address_and_port[:ip_address_and_port.rindex(':')]


if "__main__" == __name__:
    unicorn.main()

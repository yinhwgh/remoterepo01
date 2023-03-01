#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093722.001, TC0093723.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_etxchar
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles


class Test(BaseTest):
    """Check the functionality of "addrfilter" parameter. Check proper module behavior with IPv4 or IPv6 protocol stack.
    Args:
        ip_version (String): Internet Protocol version to be used. Allowed values: 'IPv4', 'IPv6'.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_enter_pin(test.dut)
        dstl_enter_pin(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on", device_interface="at2")
        dstl_set_scfg_urc_dst_ifc(test.r1, device_interface="at2")
        if test.ip_version == 'IPv6':
            test.dut.at1.send_and_verify('AT+CGPIAF=1', ".*OK.*")
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))
        test.expect(dstl_reset_internet_service_profiles(test.r1, force_reset=True))

    def run(test):
        test.log.h2("Executing test script for: TransparentTCPListenerIPAddressFilter_{}".format(test.ip_version))

        test.log.step("1) Depends on product: \n - Set Connection Profile. \n - Set and activate PDP Context Profile.")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_version=test.ip_version,
                                                                     ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, device_interface="at2",
                                                                    ip_version=test.ip_version, ip_public=True)
        test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile()

        if test.ip_version == 'IPv6':
            dummy_addresses = ['2a00:f22:ab33:0:31b6:c682:b7f0:821f', '2a00:a47:0:ff54:60b8:e765:e7f0:220c',
                               '2001:e234:cf86:0:45b1:c223:7654:551b']
        else:
            dummy_addresses = ['123.154.145.156', '125.169.212.234', '234.193.67.120']

        test.log.step("a) No address filter parameter")
        execute_steps_2_to_8(test, 'a', "", True)

        test.log.step("b) Set IP address of Remote as \"addrfilter\"")
        execute_steps_2_to_8(test, 'b', test.r1_ip_address, True)

        test.log.step("c) Set IP address of Remote as \"addrfilter\", changing last octet to \"*\"")
        separator = '.' if test.ip_version == 'IPv4' else ':'
        execute_steps_2_to_8(test, 'c', (test.r1_ip_address[:test.r1_ip_address.rindex(separator)+1])+'*', True)

        test.log.step("d) Set three parameters \"addrfilter\", none of which shall allow Remote to connect")
        execute_steps_2_to_8(test, 'd', "{},{},{}".format(dummy_addresses[0], dummy_addresses[1],
                                                          dummy_addresses[2]), False)

        test.log.step("e) Set more than 3 addresses in \"addrfilter\", put client address as 4th in \"addrfilter\"")
        execute_steps_2_to_8(test, 'e', "{},{},{},{}".format(dummy_addresses[0], dummy_addresses[1],
                                                             dummy_addresses[2], test.r1_ip_address), False)

        test.log.step("f) Set more than 3 addresses in \"addrfilter\", put client address as 3th in \"addrfilter\"")
        execute_steps_2_to_8(test, 'f', "{},{},{},{}".format(dummy_addresses[0], dummy_addresses[1],
                                                             test.r1_ip_address, dummy_addresses[2]), True)

    def cleanup(test):
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.expect(dstl_reset_internet_service_profiles(test.dut, profile_id=0, force_reset=True))
        test.expect(dstl_reset_internet_service_profiles(test.dut, profile_id=0, device_interface='at2', force_reset=True))


def execute_steps_2_to_8(test, scenario, address_filter, should_connect):
    test.log.step("2{}) Set and open TCP Transparent Listener Service Profile on DUT, "
                  "\nset Address Filtering with parameters described below (a, b, c, d, e, f).".format(scenario))
    if scenario == 'a':
        test.socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100, etx_char=26, alphabet=1, ip_version=test.ip_version)
    test.socket_dut.dstl_set_addr_filter(address_filter.replace('[', '').replace(']', ''))
    test.socket_dut.dstl_generate_address()
    test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())

    test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
    test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
    if scenario == 'a':
        test.dut_ip_address = get_ip_address(test, test.socket_dut)

    test.log.step("3{}) Set and open TCP Transparent Client Service on remote.".format(scenario))
    if scenario == 'a':
        test.socket_r1 = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(), device_interface="at2",
                                       protocol="tcp", host=test.dut_ip_address, port=65100, etx_char=26,
                                       alphabet=1, ip_version=test.ip_version)
        test.socket_r1.dstl_generate_address()
    test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())

    test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
    test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
    if scenario == 'a':
        test.r1_ip_address = get_ip_address(test, test.socket_r1)

    if should_connect:
        test.log.step("4{}) Establish transparent connection.".format(scenario))
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.expect(test.socket_dut.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.socket_r1.dstl_get_service().dstl_enter_transparent_mode())

        test.log.step("5{}) Send 10 x 100 bytes from DUT to Remote and the same amount from Remote to DUT.".format(scenario))
        data_block_size = 100
        amount_of_data_blocks = 10
        data = dstl_generate_data(data_block_size)
        test.expect(test.socket_dut.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))
        test.expect(test.socket_r1.dstl_get_service().dstl_send_data(data, expected="", repetitions=amount_of_data_blocks))

        test.log.step("6{}) Exit from transparent mode.".format(scenario))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.dut, 26))
        test.expect(dstl_switch_to_command_mode_by_etxchar(test.r1, 26, device_interface='at2'))

        test.log.step("7{}) Check service information and amount of transferred data.".format(scenario))
        test.dut.at1.read()
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTED.value)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)
        test.r1.at2.read()
        test.expect(test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("tx") == amount_of_data_blocks * data_block_size)
        test.expect(test.socket_r1.dstl_get_parser().dstl_get_service_data_counter("rx") == amount_of_data_blocks * data_block_size)
    else:
        test.log.step("4{}) Establish transparent connection.".format(scenario))
        test.expect(test.socket_r1.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48", '"Remote peer has closed the connection"'))
        test.log.h2("Steps 5-7 will be skipped for scenario: '{}'".format(scenario))

    test.log.step("8{}) Close services.".format(scenario))
    test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
    test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())

    test.log.step("9) Repeat steps from 2-8 changing Address Filter parameter.")


def get_ip_address(test, profile):
    ip_address_and_port = profile.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version=test.ip_version)
    return ip_address_and_port[:ip_address_and_port.rindex(':')]


if "__main__" == __name__:
    unicorn.main()

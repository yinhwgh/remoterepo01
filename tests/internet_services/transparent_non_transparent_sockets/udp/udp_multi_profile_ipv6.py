# responsible: dominik.tanderys@globallogic.com
# location: Wroclaw
# TC0094897.001, TC0094897.002

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses


class Test(BaseTest):
    """
    TC0094897.001, TC0094897.002 - UdpMultiProfile_IPv6
    Check 4 independent UDP IPv6 transparent and non-transparent mode connections at the same time.
     Send, receive data
    and close the connections.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True, device_interface="at2")

    def run(test):
        test.log.step("1. Enable URC mode for Internet Service commands.")

        dstl_set_scfg_tcp_with_urcs(test.dut, "on")

        test.log.step("2. Define IPv6 PDP context and activate it. (If module does not support PDP"
                      " contexts, "
                      "define connection profile).")

        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3. On 1st profile set UDP IPv6 Non-transparent Endpoint.")

        test.echo_server = EchoServer("IPv6", "UDP")
        test.endpoint = SocketProfile(test.dut, 0, cid, protocol="UDP", port="8888", alphabet="1")
        test.endpoint.dstl_generate_address()
        test.expect(test.endpoint.dstl_get_service().dstl_load_profile())

        test.log.step("4. On 2nd DUT profile set UDP IPv6 Non-transparent Client.")

        test.client_profile_1 = SocketProfile(test.dut, 1, cid, protocol="UDP", alphabet="1")
        test.client_profile_1.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client_profile_1.dstl_generate_address()
        test.expect(test.client_profile_1.dstl_get_service().dstl_load_profile())

        test.log.step("5. On 3rd DUT profile set UDP IPv6 Transparent client without etx"
                      " param set.")

        test.client_profile_2 = SocketProfile(test.dut, 2, cid, protocol="UDP", empty_etx=True,
                                              alphabet="1")
        test.client_profile_2.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client_profile_2.dstl_generate_address()
        test.expect(test.client_profile_2.dstl_get_service().dstl_load_profile())

        test.log.step("6. On 4th DUT profile set UDP IPv6 Transparent client with etx param set.")

        test.client_profile_3 = SocketProfile(test.dut, 3, cid, protocol="UDP", etx_char="26",
                                              device_interface="at2"
                                              , alphabet="1")
        test.client_profile_3.dstl_set_parameters_from_ip_server(test.echo_server)
        test.client_profile_3.dstl_generate_address()
        test.expect(test.client_profile_3.dstl_get_service().dstl_load_profile())

        test.log.step("7. Open all profiles.")
        test.expect(test.endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sis_urc_appeared(5))

        test.expect(test.client_profile_1.dstl_get_service().dstl_open_service_profile())
        test.expect(test.client_profile_1.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.expect(test.client_profile_2.dstl_get_service().dstl_open_service_profile())
        test.expect(test.client_profile_2.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.expect(test.client_profile_3.dstl_get_service().dstl_open_service_profile())
        test.expect(test.client_profile_3.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("8. Send and receive data on each profile and check the amount of data.")

        data_amount = 1460

        host_port_ipv6 = "[{}]:{}".format(test.echo_server.dstl_get_server_ip_address(),
                                          test.echo_server.dstl_get_server_port())
        test.expect(test.endpoint.dstl_get_service().
                    dstl_send_sisw_command_and_data_UDP_endpoint(data_amount, host_port_ipv6,
                                                                 eod_flag="0"))
        test.expect(test.endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.endpoint.dstl_get_service().dstl_read_data(data_amount, repetitions=2))

        test.expect(test.client_profile_1.dstl_get_service().
                    dstl_send_sisw_command_and_data(data_amount))
        test.expect(test.client_profile_1.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.client_profile_1.dstl_get_service().dstl_read_data(data_amount,
                                                                            repetitions=2))

        test.expect(test.client_profile_2.dstl_get_service().
                    dstl_send_sisw_command_and_data(data_amount))
        test.expect(test.client_profile_2.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.client_profile_2.dstl_get_service().dstl_read_data(data_amount,
                                                                            repetitions=2))

        test.expect(test.client_profile_3.dstl_get_service().
                    dstl_send_sisw_command_and_data(data_amount))
        test.expect(test.client_profile_3.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.client_profile_3.dstl_get_service().dstl_read_data(data_amount,
                                                                            repetitions=2))

        test.check_data_amount(data_amount)

        test.log.step("9. Send data in data mode on two transparent client profiles in parallel "
                      "(using two DUT interfaces).")

        test.expect(test.client_profile_2.dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.client_profile_3.dstl_get_service().dstl_enter_transparent_mode())

        for i in range(10):
            test.expect(test.client_profile_2.dstl_get_service().
                        dstl_send_data(dstl_generate_data(146), expected=""))
            test.expect(test.client_profile_3.dstl_get_service().
                        dstl_send_data(dstl_generate_data(146), expected=""))

        test.sleep(10) #added sleep for all data to be transferred
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, "at2"))

        test.log.step("10. Check the amount of data sent/received on each profile.")

        test.check_data_amount(data_amount, data_amount * 2)


    def check_data_amount(test, amount, amount_2 = 0):
        if amount_2 == 0:
            amount_2 = amount

        test.expect(test.endpoint.dstl_get_parser().dstl_get_service_data_counter("rx") == amount)
        test.expect(test.endpoint.dstl_get_parser().dstl_get_service_data_counter("tx") == amount)

        test.expect(test.client_profile_1.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                    amount)
        test.expect(test.client_profile_1.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                    amount)

        test.expect(test.client_profile_2.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                    amount_2)
        test.expect(test.client_profile_2.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                    amount_2)

        test.expect(test.client_profile_3.dstl_get_parser().dstl_get_service_data_counter("rx") ==
                    amount_2)
        test.expect(test.client_profile_3.dstl_get_parser().dstl_get_service_data_counter("tx") ==
                    amount_2)

    def cleanup(test):
        try:
            test.log.step("11. Close all profiles.")
            test.expect(test.endpoint.dstl_get_service().dstl_close_service_profile())
            test.expect(test.client_profile_1.dstl_get_service().dstl_close_service_profile())
            test.expect(test.client_profile_2.dstl_get_service().dstl_close_service_profile())
            test.expect(test.client_profile_3.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Profiles were not created.")

        try:
            test.echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("server was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True, device_interface="at2")


if "__main__" == __name__:
    unicorn.main()
#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094896.001, TC0094896.003

import unicorn
from core.basetest import BaseTest
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses


class Test(BaseTest):
    """ Check 4 independent UDP IPv4 transparent and non-transparent mode connections at the same time.
    Send, receive data and close the connections. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.echo_server = EchoServer("IPv4", "UDP")
        test.udp_clients = []
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))

    def run(test):
        test.log.h2("Executing test script for: TC0094896.001/003 UdpMultiProfile_IPv4")

        test.log.step("1. Enable URC mode for Internet Service commands.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.step("2. Define IPv4 PDP context and activate it. (If module does not support PDP contexts, "
                      "define connection profile).")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv4")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3. On 1st profile set UDP IPv4 Non-transparent Endpoint.")
        test.udp_endpoint = SocketProfile(test.dut, 0, cid, protocol="UDP", port="8888")
        test.udp_endpoint.dstl_generate_address()
        test.expect(test.udp_endpoint.dstl_get_service().dstl_load_profile())

        test.log.step("4. On 2nd DUT profile set UDP IPv4 Non-transparent Client.")
        test.udp_clients.append(SocketProfile(test.dut, 1, cid, protocol="UDP"))
        test.udp_clients[0].dstl_set_parameters_from_ip_server(test.echo_server)
        test.udp_clients[0].dstl_generate_address()
        test.expect(test.udp_clients[0].dstl_get_service().dstl_load_profile())

        test.log.step("5. On 3rd DUT profile set UDP IPv4 Transparent client without etx param set.")
        test.udp_clients.append(SocketProfile(test.dut, 2, cid, protocol="UDP", empty_etx=True))
        test.udp_clients[1].dstl_set_parameters_from_ip_server(test.echo_server)
        test.udp_clients[1].dstl_generate_address()
        test.expect(test.udp_clients[1].dstl_get_service().dstl_load_profile())

        test.log.step("6. On 4th DUT profile set UDP IPv4 Transparent client with etx param set.")
        test.udp_clients.append(SocketProfile(test.dut, 3, cid, protocol="UDP", etx_char="26", device_interface="at2"))
        test.udp_clients[2].dstl_set_parameters_from_ip_server(test.echo_server)
        test.udp_clients[2].dstl_generate_address()
        test.expect(test.udp_clients[2].dstl_get_service().dstl_load_profile())

        test.log.step("7. Open all profiles.")
        test.expect(test.udp_endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.udp_endpoint.dstl_get_urc().dstl_is_sis_urc_appeared(5))
        for udp_client in test.udp_clients:
            test.expect(udp_client.dstl_get_service().dstl_open_service_profile())
            test.expect(udp_client.dstl_get_urc().dstl_is_sisw_urc_appeared(1))

        test.log.step("8. Send and receive data on each profile and check the amount of data.")
        data_amount = 200
        data_packages = 10
        host_address_and_port = "{}:{}".format(test.echo_server.dstl_get_server_ip_address(),
                                               test.echo_server.dstl_get_server_port())
        test.expect(test.udp_endpoint.dstl_get_service()
                    .dstl_send_sisw_command_and_data_UDP_endpoint(data_amount, host_address_and_port,
                                                                  eod_flag='0', repetitions=data_packages))
        test.expect(test.udp_endpoint.dstl_get_service().dstl_read_data(data_amount, repetitions=data_packages))
        for udp_client in test.udp_clients:
            test.expect(udp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_amount, repetitions=data_packages))
            test.expect(udp_client.dstl_get_service().dstl_read_data(data_amount, repetitions=data_packages))
        test.check_data_amount(test.udp_endpoint, data_amount * data_packages)
        test.check_data_amount(test.udp_clients[0], data_amount * data_packages)
        test.check_data_amount(test.udp_clients[1], data_amount * data_packages)
        test.check_data_amount(test.udp_clients[2], data_amount * data_packages)

        test.log.step("9. Send data in data mode on two transparent client profiles in parallel "
                      "(using two DUT interfaces).")
        test.expect(test.udp_clients[1].dstl_get_service().dstl_enter_transparent_mode())
        test.expect(test.udp_clients[2].dstl_get_service().dstl_enter_transparent_mode())
        for repetition in range(data_packages):
            test.expect(test.udp_clients[1].dstl_get_service().dstl_send_data(dstl_generate_data(data_amount), expected=""))
            test.expect(test.udp_clients[2].dstl_get_service().dstl_send_data(dstl_generate_data(data_amount), expected=""))
        test.sleep(10)
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
        test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface="at2"))

        test.log.step("10. Check the amount of data sent/received on each profile.")
        test.check_data_amount(test.udp_endpoint, data_amount * data_packages)
        test.check_data_amount(test.udp_clients[0], data_amount * data_packages)
        test.check_data_amount(test.udp_clients[1], data_amount * data_packages * 2)
        test.check_data_amount(test.udp_clients[2], data_amount * data_packages * 2)

        test.log.step("11. Close all profiles.")

    def cleanup(test):
        try:
            if not test.udp_clients[1].dstl_get_service().dstl_check_if_module_in_command_mode():
                test.expect(dstl_switch_to_command_mode_by_pluses(test.dut))
            if not test.udp_clients[2].dstl_get_service().dstl_check_if_module_in_command_mode():
                test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface="at2"))
            for udp_service in [test.udp_endpoint, test.udp_clients[0], test.udp_clients[1], test.udp_clients[2]]:
                test.expect(udp_service.dstl_get_service().dstl_close_service_profile())
                test.expect(udp_service.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Service profile object was not created.")
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")

    def check_data_amount(test, udp_service, amount):
        test.expect(udp_service.dstl_get_parser().dstl_get_service_data_counter("rx") >= amount*0.8)
        test.expect(udp_service.dstl_get_parser().dstl_get_service_data_counter("tx") == amount)


if "__main__" == __name__:
    unicorn.main()

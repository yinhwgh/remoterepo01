# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0094963.002

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    1. Enable URC mode for Internet Service commands.
    2. Define IPv6 PDP context and activate it. (If module does not support PDP contexts,
        define connection profile).
    3. On 1st profiles set UDP IPv6 Non-transparent Endpoint on DUT and UDP IPv6 Non-transparent
        Client on Remote. (Or use echo server, and not use remote module at all)
    4. On 2nd DUT profile set UDP IPv6 Non-transparent Client (Connection with UDP echo server).
    5. On 3rd DUT profile set UDP IPv6 Transparent client without etx param set
        (Connection with UDP echo server).
    6. On 4th DUT profile set UDP IPv6 Transparent client with etx param setÂ
        (Connection with UDP echo server).
    7. Open all profiles on DUT (and UDP Client profile on Remote).
    8. Send and receive data on each profile and check the amount of data.
    9. Send data in data mode on two transparent client profiles in parallel
        (using two Mux DUT interfaces).
    10. Check the amount of data sent/received on each profile.
    11. Close all profiles.
    """

    def setup(test):
        test.remap({'dut_at1': 'dut_mux_1'})
        test.remap({'dut_at2': 'dut_mux_2'})
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.reset_internet_service_profiles_on_mux_interfaces()
        test.udp_clients = []

    def run(test):
        test.log.step("1. Enable URC mode for Internet Service commands.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.step("2. Define IPv6 PDP context and activate it. (If module does not support "
                      "PDP contexts, define connection profile).")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv6")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3. On 1st profiles set UDP IPv6 Non-transparent Endpoint on DUT and UDP "
                      "IPv6 Non-transparent Client on Remote. (Or use echo server, and not use "
                      "remote module at all)")
        test.echo_server = EchoServer(ip_version="IPv6", protocol="UDP")
        test.udp_endpoint = SocketProfile(test.dut, srv_profile_id=0, con_id=cid, protocol="UDP",
                                          port="8888", alphabet="1")
        test.udp_endpoint.dstl_generate_address()
        test.expect(test.udp_endpoint.dstl_get_service().dstl_load_profile())

        test.log.step("4. On 2nd DUT profile set UDP IPv6 Non-transparent Client "
                      "(Connection with UDP echo server).")
        mux1_non_transparent_client = SocketProfile(test.dut, srv_profile_id=1, con_id=cid,
                                                    protocol="UDP", alphabet="1")
        mux1_non_transparent_client.dstl_set_parameters_from_ip_server(test.echo_server)
        mux1_non_transparent_client.dstl_generate_address()
        test.expect(mux1_non_transparent_client.dstl_get_service().dstl_load_profile())
        test.udp_clients.append(mux1_non_transparent_client)

        test.log.step("5. On 3rd DUT profile set UDP IPv6 Transparent client without etx param set "
                      "(Connection with UDP echo server).")
        mux1_transparent_client = SocketProfile(test.dut, srv_profile_id=2, con_id=cid,
                                                protocol="UDP", empty_etx=True, alphabet="1")
        mux1_transparent_client.dstl_set_parameters_from_ip_server(test.echo_server)
        mux1_transparent_client.dstl_generate_address()
        test.expect(mux1_transparent_client.dstl_get_service().dstl_load_profile())
        test.udp_clients.append(mux1_transparent_client)

        test.log.step("6. On 4th DUT profile set UDP IPv6 Transparent client with etx param set "
                      "(Connection with UDP echo server).")
        mux2_transparent_client = SocketProfile(test.dut, srv_profile_id=3, con_id=cid,
                                                protocol="UDP", etx_char="26",
                                                device_interface="at2", alphabet="1")
        mux2_transparent_client.dstl_set_parameters_from_ip_server(test.echo_server)
        mux2_transparent_client.dstl_generate_address()
        test.expect(mux2_transparent_client.dstl_get_service().dstl_load_profile())
        test.udp_clients.append(mux2_transparent_client)

        test.log.step("7. Open all profiles on DUT (and UDP Client profile on Remote).")
        test.expect(test.udp_endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.udp_endpoint.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause=5))
        for client in test.udp_clients:
            test.expect(client.dstl_get_service().dstl_open_service_profile())
            test.expect(client.dstl_get_urc().dstl_is_sisw_urc_appeared(urc_cause_id=1))

        test.log.step("8. Send and receive data on each profile and check the amount of data.")
        data_amount = 314
        host_port_ipv6 = "[{}]:{}".format(test.echo_server.dstl_get_server_ip_address(),
                                          test.echo_server.dstl_get_server_port())
        test.expect(test.udp_endpoint.dstl_get_service().
                    dstl_send_sisw_command_and_data_UDP_endpoint(data_amount,
                                                                 udp_rem_client=host_port_ipv6,
                                                                 eod_flag="0"))
        test.expect(test.udp_endpoint.dstl_get_urc().dstl_is_sisr_urc_appeared(urc_cause_id="1"))
        test.expect(test.udp_endpoint.dstl_get_service().dstl_read_data(data_amount))

        for client in test.udp_clients:
            test.expect(client.dstl_get_service().dstl_send_sisw_command_and_data(data_amount))
            test.expect(client.dstl_get_urc().dstl_is_sisr_urc_appeared(urc_cause_id="1"))
            test.expect(client.dstl_get_service().dstl_read_data(data_amount))

        for client in [test.udp_endpoint, *test.udp_clients]:
            test.check_data_amount(client, data_amount)

        test.log.step("9. Send data in data mode on two transparent client profiles in parallel "
                      "(using two Mux DUT interfaces).")
        test.mux1_parallel_send_thread = test.thread(
            mux1_transparent_client.dstl_get_service().dstl_send_sisw_command_and_data, data_amount)
        test.mux2_parallel_send_thread = test.thread(
            mux2_transparent_client.dstl_get_service().dstl_send_sisw_command_and_data, data_amount)
        test.mux1_parallel_send_thread.join()
        test.mux2_parallel_send_thread.join()
        test.expect(mux1_transparent_client.dstl_get_service().dstl_read_data(data_amount))
        test.expect(mux2_transparent_client.dstl_get_service().dstl_read_data(data_amount))

        test.log.step("10. Check the amount of data sent/received on each profile.")
        for client in [mux1_transparent_client, mux2_transparent_client]:
            test.check_data_amount(client, data_amount * 2)

        test.log.step("11. Close all profiles.")
        for client in [test.udp_endpoint, *test.udp_clients]:
            test.expect(client.dstl_get_service().dstl_close_service_profile())
        test.reset_internet_service_profiles_on_mux_interfaces()

    def cleanup(test):
        for thread in [test.mux1_parallel_send_thread, test.mux2_parallel_send_thread]:
            try:
                thread.join()
            except AttributeError:
                test.log.error("Thread was not created.")
        try:
            test.echo_server.dstl_server_close_port()
        except AttributeError:
            test.log.error("server was not created.")

    def check_data_amount(test, udp_service, amount):
        """
        Method checks that sent and received amount of data are equal to amount of data
        given in amount param.
        :param udp_service: SocketProfile object from which amount of data will be read
        :param amount: expected amount of data
        """
        test.expect(udp_service.dstl_get_parser().dstl_get_service_data_counter("rx") == amount)
        test.expect(udp_service.dstl_get_parser().dstl_get_service_data_counter("tx") == amount)

    def reset_internet_service_profiles_on_mux_interfaces(test):
        """
        Method firstly tries to reset all profiles on both mux profiles to reset profiles created on
        specific interfaces. Then runs again reset all profiles on default interface with assertion.
        If the assertion is accepted, then all profiles have been reset correctly.
        """
        dstl_reset_internet_service_profiles(test.dut, force_reset=True, device_interface="at1")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True, device_interface="at2")
        test.expect(dstl_reset_internet_service_profiles(test.dut, force_reset=True))


if "__main__" == __name__:
    unicorn.main()

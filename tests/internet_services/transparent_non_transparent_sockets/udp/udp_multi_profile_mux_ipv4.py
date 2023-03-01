# responsible: maciej.kiezel@globallogic.com
# location: Wroclaw
# TC0094954.003

import unicorn
from core.basetest import BaseTest

from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.auxiliary.restart_module import dstl_restart
from dstl.call.switch_to_command_mode import dstl_switch_to_command_mode_by_pluses
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.parser.internet_service_parser import InternetServiceParser
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """
    1. Enable URC mode for Internet Service commands.
    2. Define IPv4 PDP context and activate it. (If module does not support PDP contexts, define
        connection profile).
    3. On 1st profiles set UDP IPv4 Non-transparent Endpoint on DUT and UDP IPv4 Non-transparent
        Client on Remote.
    4. On 2nd DUT profile set UDP IPv4 Non-transparent Client (Connection with UDP echo server).
    5. On 3rd DUT profile set UDP IPv4 Transparent client without etx param set (Connection with
        UDP echo server).
    6. On 4th DUT profile set UDP IPv4 Transparent client with etx param set (Connection with
        UDP echo server).
    7. Open all profiles on DUT (and UDP Client profile on Remote).
    8. Send and receive data on each profile and check the amount of data.
    9. Send data in data mode on two transparent client profiles in parallel (using two dedicated
        Mux DUT interfaces).
    10. Check the amount of data sent/received on each profile.
    11. Close all profiles.
    """

    def setup(test):
        test.remap({'dut_at1': 'dut_mux_1'})
        test.remap({'dut_at2': 'dut_mux_2'})
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.reset_internet_service_profiles_on_mux_interfaces()
        test.echo_server = EchoServer("IPv4", "UDP")
        test.udp_clients = []

    def run(test):
        test.log.step("1. Enable URC mode for Internet Service commands.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))

        test.log.step("2. Define IPv4 PDP context and activate it. (If module does not support PDP "
                      "contexts, define connection profile).")
        connection_setup = dstl_get_connection_setup_object(
            test.dut, ip_version="IP", ip_public=True)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("3. On 1st profiles set UDP IPv4 Non-transparent Endpoint on DUT and UDP "
                      "IPv4 Non-transparent Client on Remote.")
        test.udp_endpoint = SocketProfile(
            test.dut, srv_profile_id=0, con_id=cid, protocol="UDP", port="8888")
        test.udp_endpoint.dstl_generate_address()
        test.expect(test.udp_endpoint.dstl_get_service().dstl_load_profile())
        test.log.info("########## Remote UDP client will be set up in step 7. ##########")

        test.log.step("4. On 2nd DUT profile set UDP IPv4 Non-transparent Client (Connection with "
                      "UDP echo server).")
        mux1_non_transparent_client = SocketProfile(
            test.dut, srv_profile_id=1, con_id=cid, protocol="UDP")
        mux1_non_transparent_client.dstl_set_parameters_from_ip_server(test.echo_server)
        mux1_non_transparent_client.dstl_generate_address()
        test.expect(mux1_non_transparent_client.dstl_get_service().dstl_load_profile())
        test.udp_clients.append(mux1_non_transparent_client)

        test.log.step("5. On 3rd DUT profile set UDP IPv4 Transparent client without etx param "
                      "set (Connection with UDP echo server).")
        mux1_transparent_client = SocketProfile(
            test.dut, srv_profile_id=2, con_id=cid, protocol="UDP", empty_etx=True)
        mux1_transparent_client.dstl_set_parameters_from_ip_server(test.echo_server)
        mux1_transparent_client.dstl_generate_address()
        test.expect(mux1_transparent_client.dstl_get_service().dstl_load_profile())
        test.udp_clients.append(mux1_transparent_client)

        test.log.step("6. On 4th DUT profile set UDP IPv4 Transparent client with etx param set "
                      "(Connection with UDP echo server).")
        mux2_transparent_client = SocketProfile(test.dut, srv_profile_id=3, con_id=cid,
                                                protocol="UDP", etx_char="26",
                                                device_interface="at2")
        mux2_transparent_client.dstl_set_parameters_from_ip_server(test.echo_server)
        mux2_transparent_client.dstl_generate_address()
        test.expect(mux2_transparent_client.dstl_get_service().dstl_load_profile())
        test.udp_clients.append(mux2_transparent_client)

        test.log.step("7. Open all profiles on DUT (and UDP Client profile on Remote).")
        test.expect(test.udp_endpoint.dstl_get_service().dstl_open_service_profile())
        test.expect(test.udp_endpoint.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause=5))
        for udp_client in test.udp_clients:
            test.expect(udp_client.dstl_get_service().dstl_open_service_profile())
            test.expect(udp_client.dstl_get_urc().dstl_is_sisw_urc_appeared(urc_cause_id=1))

        test.log.info("########## Defining IPv4 PDP context for remote. ##########")
        remote_connection_setup = dstl_get_connection_setup_object(test.r1, ip_version="IP")
        test.expect(remote_connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.info("########## Setting up remote UDP client from step 3. ##########")
        dut_parser = InternetServiceParser(test.dut_at1, srv_profile_id=0)
        test.dut_udp_address = dut_parser.dstl_get_service_local_address_and_port(ip_version="ipv4")
        test.r01_udp_client = SocketProfile(test.r1, srv_profile_id=1, con_id=cid, protocol="UDP")
        test.r01_udp_client.dstl_set_address(f'sockudp://{test.dut_udp_address}')
        test.expect(test.r01_udp_client.dstl_get_service().dstl_load_profile())

        test.log.info("########## Opening UDP client on remote. ########## ")
        test.expect(test.r01_udp_client.dstl_get_service().dstl_open_service_profile())
        test.expect(test.r01_udp_client.dstl_get_urc().dstl_is_sisw_urc_appeared(urc_cause_id=1))

        test.log.step("8. Send and receive data on each profile and check the amount of data.")
        data_amount = 255
        for udp_client in test.udp_clients:
            test.expect(udp_client.dstl_get_service().dstl_send_sisw_command_and_data(data_amount))
            test.expect(udp_client.dstl_get_service().dstl_read_data(data_amount))

        test.expect(test.r01_udp_client.dstl_get_service().
                    dstl_send_sisw_command_and_data(data_amount))
        test.sleep(1)
        test.expect(test.udp_endpoint.dstl_get_service().dstl_read_data(req_read_length=1))
        remote_ip_address_and_port = test.udp_endpoint.dstl_get_service().dstl_get_udp_rem_client()
        test.expect(remote_ip_address_and_port != -1, critical=True)
        test.expect(test.udp_endpoint.dstl_get_service().
                    dstl_send_sisw_command_and_data_UDP_endpoint(
                        data_amount, remote_ip_address_and_port, eod_flag="1"))
        test.expect(test.udp_endpoint.dstl_get_service().dstl_read_data(data_amount-1))
        test.expect(test.r01_udp_client.dstl_get_service().dstl_read_data(data_amount))

        for udp_client in [*test.udp_clients, test.udp_endpoint, test.r01_udp_client]:
            test.check_sent_and_received_data_amount(udp_client, data_amount)

        test.log.step("9. Send data in data mode on two transparent client profiles in parallel "
                      "(using two dedicated Mux DUT interfaces).")
        test.mux1_parallel_send_thread = test.thread(
            mux1_transparent_client.dstl_get_service().dstl_send_sisw_command_and_data, data_amount)
        test.mux2_parallel_send_thread = test.thread(
            mux2_transparent_client.dstl_get_service().dstl_send_sisw_command_and_data, data_amount)
        test.mux1_parallel_send_thread.join()
        test.mux2_parallel_send_thread.join()
        for udp_client in [mux1_transparent_client, mux2_transparent_client]:
            test.expect(udp_client.dstl_get_service().dstl_read_data(data_amount))

        test.log.step("10. Check the amount of data sent/received on each profile.")
        for udp_client in [mux1_transparent_client, mux2_transparent_client]:
            test.check_sent_and_received_data_amount(udp_client, 2 * data_amount)

        test.log.step("11. Close all profiles.")
        try:
            if not test.udp_clients[1].dstl_get_service().dstl_check_if_module_in_command_mode():
                test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface="at1"))
            if not test.udp_clients[2].dstl_get_service().dstl_check_if_module_in_command_mode():
                test.expect(dstl_switch_to_command_mode_by_pluses(test.dut, device_interface="at2"))
            if not test.udp_clients[2].dstl_get_service().dstl_check_if_module_in_command_mode():
                test.expect(dstl_switch_to_command_mode_by_pluses(test.r1))
            for udp_service in [test.udp_endpoint, *test.udp_clients, test.r01_udp_client]:
                test.expect(udp_service.dstl_get_service().dstl_close_service_profile())
        except AttributeError:
            test.log.error("Service profile object was not created.")

    def cleanup(test):
        for thread in [test.mux1_parallel_send_thread, test.mux2_parallel_send_thread]:
            try:
                thread.join()
            except AttributeError:
                test.log.error("Thread was not created.")
        try:
            if not test.echo_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        test.reset_internet_service_profiles_on_mux_interfaces()
        test.expect(dstl_reset_internet_service_profiles(test.r1))

    def check_sent_and_received_data_amount(test, udp_service, amount):
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

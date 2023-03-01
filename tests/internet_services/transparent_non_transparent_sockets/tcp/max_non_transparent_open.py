#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0092338.001, TC0092338.003

import unicorn
import random
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import \
    dstl_reset_internet_service_profiles


class Test(BaseTest):
    """Intention:
Verify if there is a possibility to open a maximum number of TCP sockets and a maximum number of UDP sockets. Check in
LM or ATC-spec how many service profiles are supported.

    description:
    1. Define internet connection as a ground for next steps.
    2. Define maximum number of TCP client profiles which could be opened in same time.
    3. Open all profiles.
    4. Select several profiles and perform data exchange with server. Use different size of data package 100/200/500/1000/max size.
    5. Close opened profiles from step 3.
    6. Delete all defined profiles from step 2.
    7. Repeat steps from 2 to 6 but use UDP client.
    8. Repeat steps from 2 to 6 but mix TCP/UDP client profiles with the same assumption as in step 2."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        test.expect(dstl_enter_pin(test.dut))
        test.ip_server_tcp = EchoServer("IPv4", "TCP")
        test.ip_server_udp = EchoServer("IPv4", "UDP")
        random.seed()
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)

    def run(test):

        test.log.step("	1. Define internet connection as a ground for next steps.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        services_type = ["tcp", "udp", "mix"]

        for service_type in services_type:
            test.log.step("2. Define maximum number of TCP client profiles which could be opened in same time.")
            socket_dut = []
            if service_type == "tcp":
                srv_type = "tcp"
                test.ip_server = test.ip_server_tcp

            elif service_type == "udp":
                srv_type = "udp"
                test.ip_server = test.ip_server_udp

            for srv_id in range(0, 10):

                if service_type == "mix":
                    if random.randint(0, 10) > 4:
                        srv_type = "udp"
                        test.ip_server = test.ip_server_udp
                    else:
                        srv_type = "tcp"
                        test.ip_server = test.ip_server_tcp

                socket_dut.append(SocketProfile(test.dut, srv_id, connection_setup_dut.dstl_get_used_cid(),
                                                     protocol=srv_type, ip_server=test.ip_server))
                socket_dut[srv_id].dstl_set_parameters_from_ip_server()
                socket_dut[srv_id].dstl_generate_address()
                test.expect(socket_dut[srv_id].dstl_get_service().dstl_load_profile())

            test.log.step("3. Open all profiles.")
            for profile in socket_dut:
                test.expect(profile.dstl_get_service().dstl_open_service_profile())

            test.log.step("4. Select several profiles and perform data exchange with server. Use different size of data"
                          " package 100/200/500/1000/max size.")
            udp_max_value = 1460
            tcp_max_value = 1500
            data_length = [100, 200, 500, 1000, tcp_max_value]
            already_used_profiles = []
            for length in data_length:
                profile_number = random.randint(0, 9)
                while profile_number in already_used_profiles:
                    profile_number = random.randint(0, 9)

                if socket_dut[profile_number]._model.protocol == "udp":
                    data_length[4] = udp_max_value
                else:
                    data_length[4] = tcp_max_value

                test.expect(socket_dut[profile_number].dstl_get_service().dstl_send_sisw_command_and_data(length))
                test.expect(socket_dut[profile_number].dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
                test.expect(socket_dut[profile_number].dstl_get_service().dstl_read_data(length))

                test.expect(socket_dut[profile_number].dstl_get_parser().dstl_get_service_data_counter("RX") ==
                            length)
                test.expect(socket_dut[profile_number].dstl_get_parser().dstl_get_service_data_counter("TX") ==
                            length)

                already_used_profiles.append(profile_number)

            test.log.step("5. Close opened profiles from step 3.")
            for profile in socket_dut:
                test.expect(profile.dstl_get_service().dstl_close_service_profile())

            test.log.step("6. Delete all defined profiles from step 2.")
            for profile in socket_dut:
                test.expect(profile.dstl_get_service().dstl_reset_service_profile())
            if service_type == "tcp":
                test.log.step("7. Repeat steps from 2 to 6 but use UDP client.")

            elif service_type == "udp":
                test.log.step("8. Repeat steps from 2 to 6 but mix TCP/UDP client profiles with the same assumption as "
                              "in step 2.")

    def cleanup(test):

        try:
            test.ip_server_tcp.dstl_server_close_port()
            test.ip_server_udp.dstl_server_close_port()
        except AttributeError:
            test.log.error("Server object was not created.")

        dstl_reset_internet_service_profiles(test.dut, force_reset=True)


if "__main__" == __name__:
    unicorn.main()

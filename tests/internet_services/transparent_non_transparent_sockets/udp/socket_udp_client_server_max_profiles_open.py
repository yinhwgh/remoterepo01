#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093534.001, TC0093534.003

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.auxiliary.ip_server.echo_server import EchoServer
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.profile_storage.dstl_reset_internet_service_profiles import dstl_reset_internet_service_profiles
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command


class Test(BaseTest):
    """ Create max numbers (total 10) of the UDP clients + UDP endpoints and open it,
    send some data between modules, check service states and close them all """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)
        test.udp_server = EchoServer("IPV4", "UDP")

    def run(test):
        test.log.info("Execution of script for TC0093534.001/003 - SocketUdpClientServerMaxProfilesOpen")

        test.log.step("1. Prepare internet connections and pdp contexts.")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        dut_ip_address = test.connection_setup_dut.dstl_get_pdp_address()[0]
        dut_con_id = test.connection_setup_dut.dstl_get_used_cid()
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())
        r1_ip_address = test.connection_setup_r1.dstl_get_pdp_address()[0]
        r1_con_id = test.connection_setup_r1.dstl_get_used_cid()

        test.log.step("2. Activate URC messages.")
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))

        test.log.step("3. Set 5 UDP clients and 5 UDP endpoints for DUT and REMOTE.")
        endpoints=[]
        clients=[]
        for profile in range(10):
            if profile < 5:
                endpoints.append(test.define_udp_service(test.dut, profile, dut_con_id))
                clients.append(test.define_udp_service(test.r1, profile, r1_con_id, dut_ip_address))
            else:
                endpoints.append(test.define_udp_service(test.r1, profile, r1_con_id))
                clients.append(test.define_udp_service(test.dut, profile, dut_con_id, r1_ip_address))

        test.log.step("4. Start UDP endpoints on DUT and REMOTE.")
        for profile in range(10):
            test.expect(endpoints[profile].dstl_get_service().dstl_open_service_profile())
            test.expect(endpoints[profile].dstl_get_urc().dstl_is_sis_urc_appeared('5'))

        test.log.step("5. Start UDP clients on DUT and REMOTE and connect to other endpoints.")
        for profile in range(10):
            test.expect(clients[profile].dstl_get_service().dstl_open_service_profile())
            test.expect(clients[profile].dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("6. Send some data between modules: from clients to endpoints, read data on endpoint.")
        for profile in range(10):
            test.expect(clients[profile].dstl_get_service().dstl_send_sisw_command_and_data(100, repetitions=5))
            test.expect(endpoints[profile].dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
            test.expect(endpoints[profile].dstl_get_service().dstl_read_data(100, repetitions=5))

        test.log.step("7. Check service state and RX/TX counters for all service profiles.")
        for profile in range(10):
            test.expect(endpoints[profile].dstl_get_parser()
                        .dstl_get_service_state(Command.SISO_WRITE) == ServiceState.UP.value)
            test.expect(clients[profile].dstl_get_parser()
                        .dstl_get_service_state(Command.SISO_WRITE) == ServiceState.UP.value)
            test.expect(endpoints[profile].dstl_get_parser()
                        .dstl_get_service_data_counter("RX", Command.SISO_WRITE) >= 100*4)
            test.expect(endpoints[profile].dstl_get_parser()
                        .dstl_get_service_data_counter("TX", Command.SISO_WRITE) == 0)
            test.expect(clients[profile].dstl_get_parser()
                        .dstl_get_service_data_counter("RX", Command.SISO_WRITE) == 0)
            test.expect(clients[profile].dstl_get_parser()
                        .dstl_get_service_data_counter("TX", Command.SISO_WRITE) == 100*5)

        test.log.step("8. Close all services.")
        for profile in range(10):
            test.expect(clients[profile].dstl_get_service().dstl_close_service_profile())
            test.expect(endpoints[profile].dstl_get_service().dstl_close_service_profile())

        test.log.step("9. Check service state for all service profiles.")
        for profile in range(10):
            test.expect(endpoints[profile].dstl_get_parser()
                        .dstl_get_service_state(Command.SISO_WRITE) == ServiceState.ALLOCATED.value)
            test.expect(clients[profile].dstl_get_parser()
                        .dstl_get_service_state(Command.SISO_WRITE) == ServiceState.ALLOCATED.value)

    def cleanup(test):
        try:
            if not test.udp_server.dstl_server_close_port():
                test.log.warn("Problem during closing port on server.")
        except AttributeError:
            test.log.error("Server object was not created.")
        dstl_reset_internet_service_profiles(test.dut, force_reset=True)
        dstl_reset_internet_service_profiles(test.r1, force_reset=True)

    def define_udp_service(test, device, profile, con_id, host=None):
        socket = SocketProfile(device, profile, con_id, protocol="udp", host=host, port=8888+profile)
        socket.dstl_generate_address()
        test.expect(socket.dstl_get_service().dstl_load_profile())
        return socket


if "__main__" == __name__:
    unicorn.main()

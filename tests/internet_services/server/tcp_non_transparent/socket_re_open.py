#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0011249.003

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin, dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.auxiliary.generate_data import dstl_generate_data


class Test(BaseTest):
    """Testing Socket-TCP, setup socket connection (client and server) and client sends data to server then close the
        connection. Open the same profile again and send some data."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)

    def run(test):
        test.log.h2("Executing test script for: TC0011249.003 SocketReOpen")

        test.log.step("1) Enter PIN and attach both modules to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Define PDP context and activate it. If remote doesnt support PDP contexts, define connection profile.")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define service profiles:\n - socket TCP server on DUT\n - socket TCP client on Remote")
        socket_listener = SocketProfile(test.dut, "0", test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                               host="listener", localport=65100)
        socket_listener.dstl_generate_address()
        test.expect(socket_listener.dstl_get_service().dstl_load_profile())
        test.log.info("Client profile will be defined in next step after opening listener service profile.")

        test.log.step("4) Open connection on DUT first.")
        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address = socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

        socket_client = SocketProfile(test.r1, "0", test.connection_setup_r1.dstl_get_used_cid(),
                               protocol="tcp", host=dut_ip_address, port=65100)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("5) Open connection on Remote.")
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("6) DUT is waiting for URC which informs about incoming connection. After it comes, "
                      "accept the connection and wait for URC which informs that data can be send.")
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        socket_server_1 = SocketProfile(test.dut, socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                      test.connection_setup_dut.dstl_get_used_cid())
        test.expect(socket_server_1.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_server_1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("7) Remote is waiting for URC indication which informs that data can be send to the server.")
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("8) Remote send 100 bytes of data to the server.")
        data_to_send = dstl_generate_data(100)
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command(100))
        test.expect(socket_client.dstl_get_service().dstl_send_data(data_to_send))

        test.log.step("9) Server wait for URC which informs about new data to read, than read all of them.")
        test.expect(socket_server_1.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(socket_server_1.dstl_get_service().dstl_read_return_data(100) == data_to_send,
                    "Data read on server is different than sent from client.")

        test.log.step("10) Client close service profile.")
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_server_1.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48", '"Remote peer has closed the connection"'))

        test.log.step("11) Check the service states on both modules.")
        test.expect(socket_server_1.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

        test.log.step("12) Open on Remote the same profile again.")
        test.dut.at1.read()
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("13) Repeat steps 6-11.")
        test.log.step("13.6) DUT is waiting for URC which informs about incoming connection. After it comes, "
                      "accept the connection and wait for URC which informs that data can be send.")
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        socket_server_2 = SocketProfile(test.dut, socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                      test.connection_setup_dut.dstl_get_used_cid())
        test.expect(socket_server_2.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_server_2.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("13.7) Remote is waiting for URC indication which informs that data can be send to the server.")
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("13.8) Remote send 100 bytes of data to the server.")
        data_to_send = dstl_generate_data(100)
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command(100))
        test.expect(socket_client.dstl_get_service().dstl_send_data(data_to_send))

        test.log.step("13.9) Server wait for URC which informs about new data to read, than read all of them.")
        test.expect(socket_server_2.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(socket_server_2.dstl_get_service().dstl_read_return_data(100) == data_to_send,
                    "Data read on server is different than sent from client.")

        test.log.step("13.10) Client close service profile.")
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("13.11) Check the service states on both modules.")
        test.expect(socket_server_1.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket_server_2.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

        test.log.step("14) Close all profiles on both modules.")
        test.expect(socket_server_2.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_server_1.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_close_service_profile())

        test.log.step("15) Check the service states on both modules again.")
        test.expect(socket_server_1.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(socket_server_2.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.ALLOCATED.value)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

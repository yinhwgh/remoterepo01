#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094638.001

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


class Test(BaseTest):
    """To check if the TCP server can re-open successfully after network disconnection."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_enter_pin(test.r1))
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)

    def run(test):
        test.log.h2("Executing test script for: TC0094638.001 IpSocketTcpReopenafternetworkDisconnect.")

        test.log.step("1. Define connection profile/PDP context (and activate if needed) for DUT and Remote.")
        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile()

        test.log.step("2. Define service profiles: socket Transparent TCP Listener on DUT, Transparent TCP Client on Remote.")
        socket_listener = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100, etx_char=26)
        socket_listener.dstl_generate_address()
        test.expect(socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address = socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

        socket_client = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(),
                                      protocol="tcp", host=dut_ip_address, port=65100, etx_char=26)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open defined socket profiles, firstly for DUT and then for Remote.")
        test.log.info("Socket on DUT module was opened in previous step.")
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("4. Accept incoming connection on DUT side.")
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("5. Send/receive some data between modules.")
        exchange_data(test, socket_listener, socket_client)
        exchange_data(test, socket_client, socket_listener)

        test.log.step("6. Disconnect the network connection on DUT using at+cops=2.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=2"))
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('0', '13', '"The network is unavailable"'))

        test.log.step("7. Check internet service state.")
        test.expect(socket_listener.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)

        test.log.step("8. Close all socket profiles on DUT and Remote.")
        test.expect(socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())

        test.log.step("9. Re-connect DUT to the network.")
        test.expect(test.dut.at1.send_and_verify("AT+COPS=0"))
        test.expect(test.connection_setup_dut.dstl_activate_internet_connection())

        test.log.step("10. Repeat steps 3-5 and check if data can be write/read successfully.")

        test.log.step("10.3. Open defined socket profiles, firstly for DUT and then for Remote.")
        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address = socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]
        socket_client.dstl_set_host(dut_ip_address)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_write_address())

        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("10.4. Accept incoming connection on DUT side.")
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("3", "0"))
        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("10.5. Send/receive some data between modules.")
        exchange_data(test, socket_listener, socket_client)
        exchange_data(test, socket_client, socket_listener)

        test.log.step("11. Close all used socket profiles.")
        test.expect(socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        pass


def exchange_data(test, socket_1, socket_2):
    block_size = 1000
    test.expect(socket_1.dstl_get_service().dstl_send_sisw_command_and_data(block_size))
    test.expect(socket_2.dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
    test.expect(socket_2.dstl_get_service().dstl_read_data(block_size))
    test.expect(socket_2.dstl_get_service().dstl_get_confirmed_read_length() == block_size)


if "__main__" == __name__:
    unicorn.main()

#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0096179.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.restart_module import dstl_restart
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Testing basic functionality of TCP socket client in non transparent mode including sending End Of Data flag"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        test.expect(dstl_enter_pin(test.dut))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_restart(test.r1))
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.expect(dstl_enter_pin(test.r1))

    def run(test):
        test.log.h2("Executing test script for: TC0096179.001 NonTranspTcpClientSendReceiveDataEod")

        test.log.step("1. Set and activate connection profile/PDP context.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define and open TCP non-transparent services: server on remote and client on DUT.")
        socket_listener = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100)
        socket_listener.dstl_generate_address()
        test.expect(socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        r1_ip_address = socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        socket_client = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                      protocol="tcp", host=r1_ip_address, port=65100)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_load_profile())

        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        socket_server = SocketProfile(test.r1, socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                        connection_setup_r1.dstl_get_used_cid())
        test.expect(socket_server.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_server.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("3. Client: Send data 1500x5 bytes.")
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1500, repetitions=5))

        test.log.step("4. Server: Wait for read URC and read data.")
        test.expect(socket_server.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(socket_server.dstl_get_service().dstl_read_data(1500, repetitions=5, delay_in_ms=2000))
        test.expect(socket_server.dstl_get_service().dstl_read_data(1500, skip_data_check=True))

        test.log.step("5. Check state and RX,TX counter.")
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("RX") == 0)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("TX") == 1500*5)

        test.log.step("6. Server: Send data 1500x4 bytes.")
        test.expect(socket_server.dstl_get_service().dstl_send_sisw_command_and_data(1500, expected="O", repetitions=4))

        test.log.step("7. Client: Wait for read URC and read data.")
        test.expect(socket_client.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(socket_client.dstl_get_service().dstl_read_data(1500, repetitions=4, delay_in_ms=2000))

        test.log.step("8. Check state and RX,TX counter.")
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("RX") == 1500 * 4)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("TX") == 1500 * 5)

        test.log.step("9. Client: send 1500x4 and 1500x1 bytes with EOD flag.")
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1500, repetitions=4))
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1500, eod_flag="1"))

        test.log.step("10. Check state.")
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.CLOSING.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("RX") == 1500 * 4)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("TX") == 1500 * 10)

        test.log.step("11. Server: Wait for read URC and read data.")
        test.expect(socket_server.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(socket_server.dstl_get_service().dstl_read_data(1500, repetitions=5, delay_in_ms=2000))

        test.log.step("12. Check state and RX,TX counter.")
        test.expect(socket_client.dstl_get_urc().dstl_is_sisr_urc_appeared("2"))
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("RX") == 1500 * 4)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("TX") == 1500 * 10)

        test.log.step("13. Close connection and delete used profiles.")
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_server.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client.dstl_get_service().dstl_reset_service_profile())
        test.expect(socket_server.dstl_get_service().dstl_reset_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

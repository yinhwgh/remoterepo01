#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0094702.001, TC0094702.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState, Command


class Test(BaseTest):
    """ To verify behavior of DCD line in TCP server service. """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)

    def run(test):
        test.log.h2("Executing test script for TC0094702.001/002 TcpServerDCDLine")

        test.log.step("1. Define PDP context for Internet services.")
        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_internet_connection_profile())

        test.log.step("2. Activate Internet service connection.")
        test.expect(conn_setup_dut.dstl_activate_internet_connection())
        test.expect(conn_setup_r1.dstl_activate_internet_connection())

        test.log.step("3. Define TCP server profile.")
        test.socket_listener = SocketProfile(test.dut, 0, conn_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                             host="listener", localport=8888)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())

        test.log.step("4. Enable DCD line indication for Internet service profiles.")
        test.expect(test.dut.at1.send_and_verify('at&c2'))

        test.log.step("5. Check DCD line.")
        test.log.info('Checking DCD line state. Expected state: OFF.')
        test.expect(not test.dut.at1.connection.cd)

        test.log.step("6. Open Socket profile.")
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("7. Check service state.")
        listener_parser = test.socket_listener.dstl_get_parser()
        test.expect(listener_parser.dstl_get_service_state() == ServiceState.CONNECTING.value)

        test.log.step("8. Check DCD line.")
        test.log.info('Checking DCD line state. Expected state: ON.')
        test.expect(test.dut.at1.connection.cd)

        test.log.step("9. Connect remote client to server.")
        dut_ip_address_and_port = listener_parser.dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")
        test.socket_client = SocketProfile(test.r1, 0, conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                           host=dut_ip_address_and_port[0], port=dut_ip_address_and_port[1])
        test.socket_client.dstl_generate_address()
        test.expect(test.socket_client.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_open_service_profile())

        test.log.step("10. Accept incoming connection on server side.")
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('1'))
        new_srv_id = test.socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id()
        test.socket_server = SocketProfile(test.dut, new_srv_id, conn_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_server.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_server.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("11. Send 2000 bytes of data from client to server.")
        test.expect(test.socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1000, repetitions=2))

        test.log.step("12. Wait for 'SISR: x,1' URC on server side.")
        test.expect(test.socket_server.dstl_get_urc().dstl_is_sisr_urc_appeared('1'))
        test.sleep(5)

        test.log.step("13. Query for the number of received bytes within internal buffers. (AT^SISR=x,0).")
        server_parser = test.socket_server.dstl_get_parser()
        test.expect(server_parser.dstl_get_peek_value_of_data_to_read() == 2000)

        test.log.step("14. Check number of received bytes (eg. AT^SISI?).")
        test.expect(server_parser.dstl_get_service_data_counter('rx', at_command=Command.SISI_READ) == 0)

        test.log.step("15. Read all received data.")
        test.expect(test.socket_server.dstl_get_service().dstl_read_data(1000, repetitions=2))

        test.log.step("16. Query for the number of received bytes within internal buffers. (AT^SISR=x,0).")
        test.expect(server_parser.dstl_get_peek_value_of_data_to_read() == 0)

        test.log.step("17. Check number of received bytes (eg. AT^SISI?).")
        test.expect(server_parser.dstl_get_service_data_counter('rx', at_command=Command.SISI_READ) == 2000)

        test.log.step("18. Close all profiles on DUT.")
        test.expect(test.socket_server.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())

        test.log.step("19. Check DCD line.")
        test.log.info('Checking DCD line state. Expected state: OFF.')
        test.expect(not test.dut.at1.connection.cd)

    def cleanup(test):
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_client.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_server.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_server.dstl_get_service().dstl_reset_service_profile())


if "__main__" == __name__:
    unicorn.main()

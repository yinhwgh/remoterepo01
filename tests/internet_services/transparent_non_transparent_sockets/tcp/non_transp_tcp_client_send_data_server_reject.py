#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0096182.001

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
    """Testing basic functionality of TCP socket client in non transparent mode.
    Check behavior in case server rejects client request."""

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
        test.log.h2("Executing test script for: TC0096182.001 NonTranspTcpClientSendDataServerReject")

        test.log.step("1. Set and activate connection profile/PDP context.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define and open TCP non-transparent server (listener) on remote.")
        socket_listener = SocketProfile(test.r1, "0", connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=65100)
        socket_listener.dstl_generate_address()
        test.expect(socket_listener.dstl_get_service().dstl_load_profile())

        test.expect(socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        r1_ip_address = socket_listener.dstl_get_parser().dstl_get_service_local_address_and_port('IPv4').split(":")[0]

        test.log.step("3. Define TCP non-transparent client services on DUT.")
        socket_client = SocketProfile(test.dut, "0", connection_setup_dut.dstl_get_used_cid(),
                                      protocol="tcp", host=r1_ip_address, port=65100)
        socket_client.dstl_generate_address()
        test.expect(socket_client.dstl_get_service().dstl_load_profile())

        test.log.step("4. Client: Open service and send data 1500x1.")
        test.expect(socket_client.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_client.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))
        test.expect(socket_client.dstl_get_service().dstl_send_sisw_command_and_data(1500))

        test.log.step("5. Server: Reject client request.")
        test.expect(socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("1"))
        socket_server = SocketProfile(test.r1, socket_listener.dstl_get_urc().dstl_get_sis_urc_info_id(), 1)
        test.expect(socket_server.dstl_get_service().dstl_disconnect_remote_client())

        test.log.step("6. Client: Wait for proper URC.")
        test.expect(socket_client.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48","\"Remote peer has closed the connection\""))

        test.log.step("7. Check state and RX, TX counter.")
        test.expect(socket_client.dstl_get_parser().dstl_get_service_state() == ServiceState.DOWN.value)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("RX") == 0)
        test.expect(socket_client.dstl_get_parser().dstl_get_service_data_counter("TX") == 1500)

        test.log.step("8. Close connection and delete used profiles.")
        test.expect(socket_client.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_client.dstl_get_service().dstl_reset_service_profile())
        test.expect(socket_listener.dstl_get_service().dstl_reset_service_profile())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

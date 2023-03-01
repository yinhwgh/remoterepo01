# responsible: grzegorz.dziublinski@globallogic.com
# location: Wroclaw
# TC0093328.003, TC0093328.004

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_lte
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import \
    dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState


class Test(BaseTest):
    """Check if client can send data after server rejects his request."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))

    def run(test):
        test.log.h2("Executing test script for TC: SocketConnectionRejectLte")

        test.log.step("1) Enter PIN and attach both modules to the network (dut module to LTE).")
        test.log.info("This will be done together with next step.")

        test.log.step("2) Define PDP context and activate it. If remote doesn't support "
                      "PDP contexts, define connection profile.")
        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_internet_connection_profile())
        test.expect(dstl_register_to_lte(test.dut))
        test.sleep(60)
        test.expect(conn_setup_dut.dstl_activate_internet_connection())
        test.expect(test.dut.at1.send_and_verify("AT+COPS?", ".*[+]COPS:.*,.*,.*,7.*OK.*"),
                    critical=True, msg='Module is not registered to LTE')
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Define service profiles:\r\n "
                      "- socket TCP server on DUT \r\n- socket TCP client on Remote")
        test.socket_dut = SocketProfile(test.dut, 0, conn_setup_dut.dstl_get_used_cid(),
                                        protocol="tcp", host="listener", localport=8888)
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.log.info("Socket TCP client on remote will be defined in step 5.")

        test.log.step("4) Open connection on DUT first.")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = test.socket_dut.dstl_get_parser()\
            .dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.log.step("5) Open connection on Remote.")
        test.socket_remote = SocketProfile(test.r1, 0, conn_setup_r1.dstl_get_used_cid(),
                                           protocol="tcp", host=dut_ip_address_and_port[0],
                                           port=dut_ip_address_and_port[1])
        test.socket_remote.dstl_generate_address()
        test.expect(test.socket_remote.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())

        test.log.step("6) DUT is waiting for URC which informs about incoming connection. "
                      "After it comes, accept the connection.")
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared('1'))
        new_srv_id = test.socket_dut.dstl_get_urc().dstl_get_sis_urc_info_id()

        test.socket_dut_1 = SocketProfile(test.dut, new_srv_id, conn_setup_dut.dstl_get_used_cid())
        test.expect(test.socket_dut_1.dstl_get_service().dstl_open_service_profile())

        test.log.step("7) Remote is waiting for URC indication which informs that data can "
                      "be send to server.")
        test.expect(test.socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("8) DUT close the connection with client.")
        test.expect(test.socket_dut_1.dstl_get_service().dstl_close_service_profile())

        test.log.step("9) Remote is waiting for indication for not accomplished connection.")
        test.expect(test.socket_remote.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48",
                        '"Remote peer has closed the connection"'))

        test.log.step("10) Remote is trying to send 50 bytes of data to server.")
        test.expect(test.socket_remote.dstl_get_service().dstl_send_sisw_command(50,
                                                                                 expected='ERROR'))

        test.log.step("11) Check the service states on both modules.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.CONNECTING.value)
        test.expect(test.socket_dut_1.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.ALLOCATED.value)
        test.expect(test.socket_remote.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.DOWN.value)

        test.log.step("12) Close all profiles.")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())

        test.log.step("13) Check the service states again.")
        test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.ALLOCATED.value)
        test.expect(test.socket_dut_1.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.ALLOCATED.value)
        test.expect(test.socket_remote.dstl_get_parser().dstl_get_service_state() ==
                    ServiceState.ALLOCATED.value)

    def cleanup(test):
        try:
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket profile object was not created.")
        try:
            test.expect(test.socket_dut_1.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dut_1.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket profile object was not created.")
        try:
            test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_remote.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket profile object was not created.")


if "__main__" == __name__:
    unicorn.main()

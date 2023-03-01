#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0092905.001, TC0092905.002

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_register_to_network
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """Check the behaviour of module when there's no empty service profile slots
    or no additional profile slots are used (depending on product)."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))

    def run(test):
        test.log.h2("Executing script for TC0092905.001/002 - TransparentTCPListenerServiceProfileNonEmpty")
        test.log.step("1) Module attaches to network")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Depends on product:\r\n- Setup Internet Connection Profile(GPRS)"
                      "\r\n - Define PDP context")
        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_internet_connection_profile())

        test.log.step("3) Set service profiles: On DUT TCP transparent listener. "
                      "On Remote set TCP transparent client.")
        test.socket_listener = SocketProfile(test.dut, 0, conn_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                             host="listener", localport=8888, etx_char=26)
        test.socket_listener.dstl_generate_address()
        test.expect(test.socket_listener.dstl_get_service().dstl_load_profile())
        test.sockets_dut = [test.socket_listener]
        test.log.info("Client profile will be defined after opening listener profile.")

        test.log.step("4) Depends on product: \r\n- Activate PDP Context ")
        test.expect(conn_setup_dut.dstl_activate_internet_connection())
        test.expect(conn_setup_r1.dstl_activate_internet_connection())

        test.log.step("5) Open services: listener on DUT and client on Remote.")
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
        dut_ip_address_and_port = test.socket_listener.dstl_get_parser(). \
            dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.socket_remote = SocketProfile(test.r1, 0, conn_setup_r1.dstl_get_used_cid(), protocol="tcp", etx_char=26,
                                           host=dut_ip_address_and_port[0], port=dut_ip_address_and_port[1])
        test.socket_remote.dstl_generate_address()
        test.expect(test.socket_remote.dstl_get_service().dstl_load_profile())

        test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("6) Accept incoming connection on DUT.")
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('3'))
        test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_listener.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        for iteration in range(1, 10):
            test.log.step("7) Close service on Remote and open it again. Accept incoming connection on DUT. "
                          "Repeat this step 9 times.\r\n Iteration no: {}".format(iteration))
            test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_listener.dstl_get_urc().
                        dstl_is_sis_urc_appeared('0', '48', '"Remote peer has closed the connection"'))
            test.expect(test.socket_remote.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))
            test.expect(test.socket_listener.dstl_get_urc().dstl_is_sis_urc_appeared('3'))
            test.expect(test.socket_listener.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_listener.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

    def cleanup(test):
        test.log.step("8) Close services.")
        test.expect(test.socket_remote.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_remote.dstl_get_service().dstl_reset_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_listener.dstl_get_service().dstl_reset_service_profile())


if "__main__" == __name__:
    unicorn.main()

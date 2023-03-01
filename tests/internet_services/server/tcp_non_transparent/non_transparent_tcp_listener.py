#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0104462.001

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
    """Basic test of Non-transparent TCP Listener"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))

    def run(test):
        test.log.step("1) Enter PIN and attach module to the network.")
        test.expect(dstl_register_to_network(test.dut))
        test.expect(dstl_register_to_network(test.r1))

        test.log.step("2) Depends on product: \r\n - Setup Internet Connection Profile (GPRS) \r\n - Define PDP context and activate it")
        conn_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(conn_setup_dut.dstl_load_and_activate_internet_connection_profile())
        conn_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(conn_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("3) Set service profiles: \r\n - TCP non transparent listener on DUT. \r\n - TCP non transparent client on Remote.")
        socket_dut = SocketProfile(test.dut, 0, conn_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=8888)
        socket_dut.dstl_generate_address()
        test.expect(socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        dut_ip_address_and_port = socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")
        socket_remote = SocketProfile(test.r1, 0, conn_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                           host=dut_ip_address_and_port[0], port=dut_ip_address_and_port[1])
        socket_remote.dstl_generate_address()
        test.expect(socket_remote.dstl_get_service().dstl_load_profile())

        test.log.step("4) Open services: listener on DUT then client on Remote.")
        test.log.info("Listener service on DUT opened in previous step to get IP address.")
        test.expect(socket_remote.dstl_get_service().dstl_open_service_profile())

        test.log.step("5) Accept incoming connection on DUT.")
        test.expect(socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared('1'))

        new_srv_id = socket_dut.dstl_get_urc().dstl_get_sis_urc_info_id()

        socket_dut_1 = SocketProfile(test.dut, new_srv_id, conn_setup_dut.dstl_get_used_cid())
        test.expect(socket_dut_1.dstl_get_service().dstl_open_service_profile())

        test.log.step("6) Wait for write URC on client.")
        test.expect(socket_remote.dstl_get_urc().dstl_is_sisw_urc_appeared('1'))

        test.log.step("7) Close services on DUT and Remote.")
        test.expect(socket_dut_1.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_dut.dstl_get_service().dstl_close_service_profile())
        test.expect(socket_remote.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

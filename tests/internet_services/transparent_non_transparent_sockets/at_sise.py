#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0095696.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc


class Test(BaseTest):
    """Intention:
    Check basic AT^SISE functionality<

    description:
    1. Define PDP context and activate
    2. Define and open TCP listener service on remote.
    3. Define and open TCP client on DUT, set tcpOT parameter to 60
    4. Accept client connection on listener side.
    5. Check ERROR reports (SISE) on DUT
    6. Send some data from client and read data on server side
    7. Check ERROR reports (SISE) on DUT
    8. Close service on server side and wait for URC on client
    9. Check ERROR reports (SISE) on DUT
    10. Close all services
    11. Check ERROR reports (SISE) on DUT
    12. Open client service and wait for proper URC
    13. Check ERROR reports (SISE) on DUT
    14. Close client service"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        dstl_set_scfg_tcp_with_urcs(test.r1, "on")
        dstl_set_scfg_urc_dst_ifc(test.r1)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(dstl_enter_pin(test.r1))

    def run(test):
        test.log.info("TC0095696.001 - AtSise")
        test.log.step("1. Define PDP context and activate")

        test.connection_setup_dut = dstl_get_connection_setup_object(test.dut)
        test.expect(test.connection_setup_dut.dstl_load_and_activate_internet_connection_profile())

        test.connection_setup_r1 = dstl_get_connection_setup_object(test.r1, ip_public=True)
        test.expect(test.connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        test.log.step("2. Define and open TCP listener service on remote.")
        test.socket_rem = SocketProfile(test.r1, 0, test.connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                        host="listener", localport=8888, etx_char="26")

        test.socket_rem.dstl_generate_address()
        test.socket_rem.dstl_get_service().dstl_load_profile()

        test.expect(test.socket_rem.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_rem.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))

        test.log.step("3. Define and open TCP client on DUT, set tcpOT parameter to 60")
        rem_ip = test.socket_rem.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")

        test.socket_dut = SocketProfile(test.dut, 0, test.connection_setup_dut.dstl_get_used_cid(),
                                            protocol="tcp", host=rem_ip[0], port=rem_ip[1], tcp_ot="60")
        test.socket_dut.dstl_generate_address()
        test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

        test.log.step("4. Accept client connection on listener side.")
        test.expect(test.socket_rem.dstl_get_urc().dstl_is_sis_urc_appeared())
        test.expect(test.socket_rem.dstl_get_service().dstl_open_service_profile())

        test.log.step("5. Check ERROR reports (SISE) on DUT")
        test.expect(test.dut.at1.send_and_verify("AT^SISE=0", "SISE: 0,0"))

        test.log.step("6. Send some data from client and read data on server side")
        test.expect(test.socket_dut.dstl_get_service().dstl_send_sisw_command_and_data(10))

        test.expect(test.socket_rem.dstl_get_urc().dstl_is_sisr_urc_appeared("1"))
        test.expect(test.socket_rem.dstl_get_service().dstl_read_data(10))

        test.log.step("7. Check ERROR reports (SISE) on DUT")
        test.expect(test.dut.at1.send_and_verify("AT^SISE=0", "SISE: 0,0"))

        test.log.step("8. Close service on server side and wait for URC on client")
        test.expect(test.socket_rem.dstl_get_service().dstl_close_service_profile())
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("0", "48",
                                                                            "\"Remote peer has closed the connection\""))

        test.log.step("9. Check ERROR reports (SISE) on DUT")
        test.expect(test.dut.at1.send_and_verify("AT^SISE=0", "0,48,\"Remote peer has closed the connection\""))

        test.log.step("10. Close all services")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

        test.log.step("11. Check ERROR reports (SISE) on DUT")
        test.expect(test.dut.at1.send_and_verify("AT^SISE=0", "SISE: 0,0"))

        test.log.step("12. Open client service and wait for proper URC")
        test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("0", "20",
                                                                            "\"Connection timed out\"", timeout=90))

        test.log.step("13. Check ERROR reports (SISE) on DUT")
        test.expect(test.dut.at1.send_and_verify("AT^SISE=0", "0,20,\"Connection timed out\""))

        test.log.step("14. Close client service")
        test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

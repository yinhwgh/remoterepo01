#responsible: grzegorz.dziublinski@globallogic.com
#location: Wroclaw
#TC0093547.001, TC0093547.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.configuration.scfg_urc_dst_ifc import dstl_set_scfg_urc_dst_ifc
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.internet_service.parser.internet_service_parser import ServiceState
from time import time


class Test(BaseTest):
    """ Check connectiontimeout parameter on listener. Connection timeout specifies the time
    after which incoming client are rejected automatically."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.dut, "on"))
        dstl_detect(test.r1)
        dstl_get_imei(test.r1)
        test.expect(dstl_set_scfg_tcp_with_urcs(test.r1, "on"))
        test.expect(dstl_set_scfg_urc_dst_ifc(test.r1))

    def run(test):
        test.log.info("Executing script for test case: 'TC0093547.001/002 SocketListenerParamConnectionTimeout'")
        connect_timeout_values = [30, 60, 180]

        test.log.step("1) Define PDP context and activate it. If module doesn't "
                      "support PDP contexts, define connection profile.")
        connection_setup_dut = dstl_get_connection_setup_object(test.dut, ip_public=True)
        test.expect(connection_setup_dut.dstl_load_and_activate_internet_connection_profile())
        connection_setup_r1 = dstl_get_connection_setup_object(test.r1)
        test.expect(connection_setup_r1.dstl_load_and_activate_internet_connection_profile())

        for connect_timeout in connect_timeout_values:
            if connect_timeout != 30:
                test.log.step("Repeat steps 2-9, but use connection timeout set to {} s.".format(connect_timeout))

            test.log.step("2) Define socket Transparent TCP listener on DUT with connecttimeout "
                          "parameter set to {} and open service.".format(connect_timeout))
            test.socket_dut = SocketProfile(test.dut, '1', connection_setup_dut.dstl_get_used_cid(), protocol="tcp",
                                            host="listener", localport=65000, etx_char=26, connect_timeout=connect_timeout)
            test.socket_dut.dstl_generate_address()
            test.expect(test.socket_dut.dstl_get_service().dstl_load_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_open_service_profile())
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared("5\r\n"))
            dut_ip_address = test.socket_dut.dstl_get_parser().dstl_get_service_local_address_and_port(ip_version='IPv4').split(":")[0]

            test.log.step("3) Define socket Transparent TCP client on Remote and open service.")
            test.socket_r1 = SocketProfile(test.r1, '1', connection_setup_r1.dstl_get_used_cid(), protocol="tcp",
                                           host=dut_ip_address, port=65000, etx_char=26)
            test.socket_r1.dstl_generate_address()
            test.expect(test.socket_r1.dstl_get_service().dstl_load_profile())

            test.expect(test.socket_r1.dstl_get_service().dstl_open_service_profile())

            test.log.step("4) Wait for proper URC on remote, which informs that data can be send.")
            test.expect(test.socket_r1.dstl_get_urc().dstl_is_sisw_urc_appeared("1"))

            test.log.step("5) Wait for proper URC on listener, which informs about incoming connection "
                          "- don't accept the connection.")
            test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared('3', '0'))
            start_time = time()

            test.log.step("6) Check service state on listener.")
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.ALERTING.value)

            test.log.step("7) Wait about {} seconds for URC which informs that connection "
                          "was rejected by server.".format(connect_timeout))
            if test.expect(test.socket_dut.dstl_get_urc().dstl_is_sis_urc_appeared('4', '0', timeout=connect_timeout*2),
                           msg="Expected URC not appeared."):
                urc_end_time = int(time() - start_time)
                test.log.info("URC appeared after {} seconds. "
                              "Expected value: {} seconds.".format(urc_end_time, connect_timeout))
                test.expect(abs(urc_end_time - connect_timeout) < connect_timeout/10,
                            msg="URC appeared, but not in expected time.")

            test.log.step("8) Check service state on listener.")
            test.expect(test.socket_dut.dstl_get_parser().dstl_get_service_state() == ServiceState.UP.value)

            test.log.step("9) Close all connections on dut and remote.")
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        try:
            test.expect(test.socket_dut.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_dut.dstl_get_service().dstl_reset_service_profile())
            test.expect(test.socket_r1.dstl_get_service().dstl_close_service_profile())
            test.expect(test.socket_r1.dstl_get_service().dstl_reset_service_profile())
        except AttributeError:
            test.log.error("Socket profile object was not created.")


if "__main__" == __name__:
    unicorn.main()

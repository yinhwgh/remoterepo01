#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
# TC0102567.001

import unicorn
from core.basetest import BaseTest
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import dstl_set_scfg_tcp_with_urcs
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.internet_service.profile.socket_profile import SocketProfile


class Test(BaseTest):
    """
    Test check whether the same report status appear in ^SISE as by ^SIS: URC.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut), critical=True)

    def run(test):
        test.log.info("Executing script for test case: TC0102567.001AtSiseUDP_Basic")
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")
        connection_setup_object = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())


        test.log.step("1) Create UDP Client profile using not existing UDPS server in address field"
                      " (eg.: address,sockudps://192.100.100.100:65000")
        test.socket = SocketProfile(test.dut, 1, connection_setup_object.dstl_get_used_cid(),
                                    host="192.100.100.100", port=65000, protocol="udp", secure_connection=True)
        test.socket.dstl_set_secopt("0")
        test.socket.dstl_generate_address()
        test.expect(test.socket.dstl_get_service().dstl_load_profile())

        test.log.step("2) Open service.")
        test.expect(test.socket.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))

        test.log.step("3) Wait for URC closing service ^SIS")
        test.expect(test.socket.dstl_get_urc().dstl_is_sis_urc_appeared(urc_cause="0", timeout=180))

        test.log.step("4) Read error report by AT^SISE=x")
        test.expect(test.dut.at1.send_and_verify("At^SISE=1", "{},\"{}".
                                                 format(test.socket.dstl_get_urc().dstl_get_sis_urc_info_id(),
                                                        test.socket.dstl_get_urc().dstl_get_sis_urc_info_text())))

        test.log.step("5) Check test command")
        test.expect(test.dut.at1.send_and_verify("At^SISE=?", ".*OK.*"))

    def cleanup(test):
        test.log.step("6) Close service")
        test.expect(test.socket.dstl_get_service().dstl_close_service_profile())

if "__main__" == __name__:
    unicorn.main()

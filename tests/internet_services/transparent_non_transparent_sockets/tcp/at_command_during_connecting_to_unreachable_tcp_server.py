#responsible: tomasz.brzyk@globallogic.com
#location: Wroclaw
#TC0104247.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.parser.internet_service_parser import ServiceState
from dstl.internet_service.profile.socket_profile import SocketProfile
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.configuration.scfg_tcp_with_urcs import *
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):
    """	Checking behavior of module during connecting to unreachable TCP server - IPIS100283446"""

    def setup(test):
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_scfg_tcp_with_urcs(test.dut, "on")


    def run(test):
        test.log.h2("TC0104247.001 AtCommandDuringConnectingToUnreachableTcpServer")

        test.log.step("1.Depends on product:\n - Set PDP context activate it.\n - Define Internet Connection Profile.")
        connection_setup = dstl_get_connection_setup_object(test.dut)
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        cid = connection_setup.dstl_get_used_cid()

        test.log.step("2. Set TCP Client service profile to unreachable Server address.")
        client_profile = SocketProfile(test.dut, 1, cid, protocol="TCP", address="192.168.201.7:666")
        client_profile.dstl_generate_address()
        test.expect(client_profile.dstl_get_service().dstl_load_profile())

        test.log.step("3. Open service and try to execute AT command:\n-AT^SISO?\n-AT^SISS?\n-AT^SCFG?")
        test.expect(client_profile.dstl_get_service().dstl_open_service_profile(wait_for_default_urc=False))
        test.expect(client_profile.dstl_get_parser().dstl_get_service_state() == ServiceState.CONNECTING.value)
        test.expect(test.dut.at1.send_and_verify('at^siss?', expect="OK", wait_for="OK", timeout=10))
        test.expect(dstl_get_scfg_tcp_with_urcs(test.dut, False))

        test.log.step("4. Close service (AT^SISC=<srvProfileId>)")
        test.expect(client_profile.dstl_get_service().dstl_close_service_profile())

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

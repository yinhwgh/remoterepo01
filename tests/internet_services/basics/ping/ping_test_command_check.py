#responsible: dominik.tanderys@globallogic.com
#location: Wroclaw
#TC0094243.001, TC0094243.002

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    """	Execute ping test and read command. Check response of those commands."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_restart(test.dut))

    def run(test):
        test.log.info("TC0094243.001, TC0094243.001 - PingTestCommandCheck")

        test.log.step("1. Check supported  conProfileIds by command AT+CGDCONT=?")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?", "OK"))
        test.expect("+CGDCONT: (1-16)" in test.dut.at1.last_response)

        test.log.step("2. Enter PIN to enable SISX commands.")
        test.expect(dstl_enter_pin(test.dut))

        test.log.step("3. Execute ping test command AT^SISX=?")
        test.expect(test.dut.at1.send_and_verify('at^sisx=?', 'OK'))

        test.expect("^SISX: \"Ping\",(1-16),,(1-30),(200-10000)" in test.dut.at1.last_response)
        test.expect("^SISX: \"HostByName\",(1-16)" in test.dut.at1.last_response)
        test.expect("^SISX: \"Ntp\",(1-16)" in test.dut.at1.last_response)

        test.log.step("4. Execute ping read command AT^SISX?")
        test.expect(test.dut.at1.send_and_verify('at^sisx?', 'ERROR'))

        test.log.step("5. Activate PDP context. (Skip if PDP context was activated after entering the pin)")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv4")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())

        test.log.step("6. Once again check supported  conProfileIds by command AT+CGDCONT=?")
        test.expect(test.dut.at1.send_and_verify("AT+CGDCONT=?", "OK"))
        test.expect("+CGDCONT: (1-16)" in test.dut.at1.last_response)

        test.log.step("7. Execute ping test command AT^SISX=?")
        test.expect(test.dut.at1.send_and_verify('at^sisx=?', 'OK'))

        test.expect("^SISX: \"Ping\",(1-16),,(1-30),(200-10000)" in test.dut.at1.last_response)
        test.expect("^SISX: \"HostByName\",(1-16)" in test.dut.at1.last_response)
        test.expect("^SISX: \"Ntp\",(1-16)" in test.dut.at1.last_response)

        test.log.step("8. Execute ping read command AT^SISX?")
        test.expect(test.dut.at1.send_and_verify('at^sisx?', 'ERROR'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

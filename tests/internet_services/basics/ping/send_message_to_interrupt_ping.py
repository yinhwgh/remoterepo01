#responsible: maciej.gorny@globallogic.com
#location: Wroclaw
#TC0096306.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object


class Test(BaseTest):
    """To check if PING process could be interrupted by AT command or any character input."""

    def setup(test):
        dstl_detect(test.dut)
        dstl_enter_pin(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.h2("TC0096306.001 SendMessageToInterruptPING'")

        test.log.step("1. Configure module to support an available band and register to network..")
        connection_setup = dstl_get_connection_setup_object(test.dut, ip_version="IPv4")
        test.expect(connection_setup.dstl_load_and_activate_internet_connection_profile())
        test_result_pass = True

        test.log.step("2. Start PING command to access target address continuously./n"
                      "For example: set the to the maximum number in AT^SISX=, ,[, [, ")
        try:
            ip_address = test.tcp_echo_server_ipv4
        except AttributeError:
            ip_address = test.ssh_server.host
        cid = connection_setup.dstl_get_used_cid()
        test.dut.at1.send("AT^SISX=PING,{},{},30".format(cid, ip_address))
        test.expect(test.dut.at1.wait_for("^SISX:", timeout=10))

        test.log.step("3. During PING process, send a 'at' from serial port.")
        test.dut.at1.send("AT")
        if test.dut.at1.wait_for(".*2,{},30,[0-30].*".format(cid), timeout=45):
            test.log.error("Ping executed correctly - incorrect")
            test_result_pass = False
        else:
            test.log.h2("Ping interrupted correctly by AT command")
        test.log.info("Additional AT command to clear the buffer added")
        test.expect(test.dut.at1.send_and_verify("AT", ".*OK"))
        test.sleep(10)

        test.log.step("4. Resume the PING process again.")
        test.dut.at1.send("AT^SISX=PING,{},{},30".format(cid, ip_address))
        test.expect(test.dut.at1.wait_for("^SISX:", timeout=10))

        test.log.step("5. During PING process, input any character from serial port.")
        test.dut.at1.send("X")
        if test.dut.at1.wait_for(".*2,{},30,[0-30].*".format(cid), timeout=45):
            test.log.error("Ping executed correctly - incorrect")
            test_result_pass = False
        else:
            test.log.h2("Ping interrupted correctly by AT command")
        if not test_result_pass:
            test.fail()

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

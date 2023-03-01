#responsible maciej.gorny@globallogic.com
#location Wroclaw
#corresponding Test Case TC 0102386.001
import unicorn
from core.basetest import BaseTest
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.auxiliary.init import dstl_detect
from dstl.internet_service.connection_setup_service.connection_setup_service import dstl_get_connection_setup_object



class Test(BaseTest):
    """Short description:
       	Check IPv6 address conversion

       Detailed description:
       1. Enable an IPv6 or IPv4v6 PDP context
       2. Set cgpiaf to 0.
       3. Check IPv6 address.
       4. Set cgpiaf to 1.
       5. Check if IPv6 address is converted properly.
       """
    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))

    def run(test):
        test.log.h2("Executing script for test case: TC0102386.001 IPv6AddressConversion")
        connection_setup_object = dstl_get_connection_setup_object(test.dut, ip_version="IPV6")

        test.log.step("1) Enable an IPv6 or IPv4v6 PDP context")
        test.expect(connection_setup_object.dstl_load_and_activate_internet_connection_profile())
        expected = ".*OK.*"
        regex_ipv6_dot_notation = (r".*.[\d.]{20,100}.*")
        regex_ipv6_colon_notation = (r".*[\w:]{20,100}.*")

        test.log.step("2) Set cgpiaf to 0.")
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=0", expected))

        test.log.step("3) Check IPv6 address.")
        test.dut.at1.send("AT+CGPADDR")
        test.expect(test.dut.at1.wait_for(regex_ipv6_dot_notation))

        test.log.step("4) Set cgpiaf to 1.")
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=1", expected))

        test.log.step("5) Check if IPv6 address is converted properly.")
        test.dut.at1.send("AT+CGPADDR")
        test.expect(test.dut.at1.wait_for(regex_ipv6_colon_notation))

    def cleanup(test):
        test.expect(test.dut.at1.send_and_verify("AT+CGPIAF=0", ".*OK.*"))

    if "__main__" == __name__:
        unicorn.main()

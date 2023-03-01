# responsible sebastian.lupkowski@globallogic.com
# Wroclaw
# TC 0104834.001
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_imei import dstl_get_imei
from dstl.network_service.register_to_network import dstl_enter_pin


class Test(BaseTest):
    """
    TC0104834.001    IPv6AddressConversionCgpiaf

    Check if module is capable of IPv6 address conversion

    Part 1:
        Step 1: set AT+CGPIAF=1,0,0,0
        Step 2: set new PDP context with IPv4 in IPv6 address:
            a) e.g. at+cgdcont=5,"IPV6","int","0:0:0:0:0:ffff:808:808"
            b) e.g. at+cgdcont=6,"IPV6","int","0:0:0:0:0:FFFF:8.8.8.8"
        Step 3: check if contexts are saved correctly - both contexts should have IPv6 address in
            "0:0:0:0:0:ffff:808:808" format
        Step 4: set AT+CGPIAF=1,0,1,1
        Step 5: check contexts again - both contexts should have IPv6 address in "::ffff:8.8.8.8" format
        Step 6: set AT+CGPIAF=0 \n"
        Step 7: check if both given IPv6 addreses change to "0.0.0.0.0.0.0.0.0.0.255.255.8.8.8.8"
    Part 2:
        Step 1: set AT+CGPIAF=1
        Step 2: set new PDP context with IPv6 address with some ":0000:" segments " +
            e.g. at+cgdcont=7,"IPV6","inter","2001:0DB8:0000:CD30:0000:0000:0000:0000"
        Step 3: set AT+CGPIAF=1,0,0,0
        Step 4: check if given address changes to "2001:db8:0:cd30:0:0:0:0"
        Step 5: set AT+CGPIAF=1,0,1,0
        Step 6: check if given address changes to "2001:0db8:0000:cd30:0000:0000:0000:0000"
        Step 7: set AT+CGPIAF=1,0,1,1
        Step 8: check if given address changes to "2001:0db8:0000:cd30::"
        Step 9: set AT+CGPIAF=1,0,0,1
        Step 10: check if given address changes to "2001:db8:0:cd30::"
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        test.log.step("Part 1:")
        test.log.step("Step 1: set AT+CGPIAF=1,0,0,0")
        set_cgpiaf(test, "1,0,0,0")

        test.log.step("Step 2: set new PDP context with IPv4 in IPv6 address:")
        test.log.step("a) e.g. at+cgdcont=5,\"IPV6\",\"int1\",\"0:0:0:0:0:ffff:808:808\"")
        set_cgdcont(test, "5,\"IPV6\",\"int1\",\"0:0:0:0:0:ffff:808:808\"")
        test.log.step("b) e.g. at+cgdcont=6,\"IPV6\",\"int2\",\"0:0:0:0:0:FFFF:8.8.8.8\"")
        set_cgdcont(test, "6,\"IPV6\",\"int2\",\"0:0:0:0:0:FFFF:8.8.8.8\"")

        test.log.step("Step 3: check if contexts are saved correctly - both contexts should have IPv6 address in "
                      "\"0:0:0:0:0:ffff:808:808\" format")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 5,\"IPV6\",\"int1\",\"0:0:0:0:0:0:0:0\".*CGDCONT: 6,\"IPV6\","
                                "\"int2\",\"0:0:0:0:0:0:0:0\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 5,\"IPV6\",\"int1\",\"0:0:0:0:0:ffff:808:808\".*CGDCONT: 6,\"IPV6\","
                                "\"int2\",\"0:0:0:0:0:ffff:808:808\".*OK.*")

        test.log.step("Step 4: set AT+CGPIAF=1,0,1,1")
        set_cgpiaf(test, "1,0,1,1")

        test.log.step("Step 5: check contexts again - both contexts should have IPv6 address in "
                      "\"::ffff:8.8.8.8\" format")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 5,\"IPV6\",\"int1\",\"::\".*CGDCONT: 6,\"IPV6\","
                                "\"int2\",\"::\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 5,\"IPV6\",\"int1\",\"::ffff:8.8.8.8\".*CGDCONT: 6,\"IPV6\",\"int2\","
                            "\"::ffff:8.8.8.8\".*OK.*")

        test.log.step("Step 6: set AT+CGPIAF=0")
        set_cgpiaf(test, "0")

        test.log.step("Step 7: check if both given IPv6 addreses change to \"0.0.0.0.0.0.0.0.0.0.255.255.8.8.8.8\"")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 5,\"IPV6\",\"int1\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\".*CGDCONT: "
                                "6,\"IPV6\",\"int2\",\"0.0.0.0.0.0.0.0.0.0.0.0.0.0.0.0\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 5,\"IPV6\",\"int1\",\"0.0.0.0.0.0.0.0.0.0.255.255.8.8.8.8\".*CGDCONT: 6,"
                            "\"IPV6\",\"int2\",\"0.0.0.0.0.0.0.0.0.0.255.255.8.8.8.8\".*OK.*")

        test.log.step("Part 2:")
        test.log.step("Step 1: set AT+CGPIAF=1")
        set_cgpiaf(test, "1")

        test.log.step("Step 2: set new PDP context with IPv6 address with some \":0000:\" segments "
                      "e.g. at+cgdcont=7,\"IPV6\",\"inter\",\"2001:0DB8:0000:CD30:0000:0000:0000:0000\"")
        set_cgdcont(test, "7,\"IPV6\",\"inter\",\"2001:0DB8:0000:CD30:0000:0000:0000:0000\"")

        test.log.step("Step 3: set AT+CGPIAF=1,0,0,0")
        set_cgpiaf(test, "1,0,0,0")

        test.log.step("Step 4: check if given address changes to \"2001:db8:0:cd30:0:0:0:0\"")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"0:0:0:0:0:0:0:0\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"2001:db8:0:cd30:0:0:0:0\".*OK.*")

        test.log.step("Step 5: set AT+CGPIAF=1,0,1,0")
        set_cgpiaf(test, "1,0,1,0")

        test.log.step("Step 6: check if given address changes to \"2001:0db8:0000:cd30:0000:0000:0000:0000\"")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"0000:0000:0000:0000:0000:0000:0000:0000\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"2001:0db8:0000:cd30:0000:0000:0000:0000\".*OK.*")

        test.log.step("Step 7: set AT+CGPIAF=1,0,1,1")
        set_cgpiaf(test, "1,0,1,1")

        test.log.step("Step 8: check if given address changes to \"2001:0db8:0000:cd30::\"")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"::\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"2001:0db8:0000:cd30::\".*OK.*")

        test.log.step("Step 9: set AT+CGPIAF=1,0,0,1")
        set_cgpiaf(test, "1,0,0,1")

        test.log.step("Step 10: check if given address changes to \"2001:db8:0:cd30::\"")
        if test.dut.product.upper() == "EXS82":
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"::\".*OK.*")
        else:
            check_cgdcont(test, ".*CGDCONT: 7,\"IPV6\",\"inter\",\"2001:db8:0:cd30::\".*OK.*")

    def cleanup(test):
        set_cgdcont(test, '5')
        set_cgdcont(test, '6')
        set_cgdcont(test, '7')
        set_cgpiaf(test, '0')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def set_cgpiaf(test, settings):
    test.expect(test.dut.at1.send_and_verify('AT+CGPIAF={}'.format(settings), '.*OK.*'))


def set_cgdcont(test, settings):
    test.expect(test.dut.at1.send_and_verify('AT+CGDCONT={}'.format(settings), '.*OK.*'))


def check_cgdcont(test, response):
    test.expect(test.dut.at1.send_and_verify('AT+CGDCONT?', '.*{}.*'.format(response)))


if "__main__" == __name__:
    unicorn.main()

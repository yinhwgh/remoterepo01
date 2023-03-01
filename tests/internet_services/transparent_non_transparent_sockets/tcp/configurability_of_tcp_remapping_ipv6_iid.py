#responsible: damian.latacz@globallogic.com
#location: Wroclaw
#TC0105390.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    TC intention: To check if Static IPv6 Address Allocation could be set on module and if setting is non-volatile.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.step("1. Execute the scfg=? (test) command and check output.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=?"))
        test.expect("\"Tcp/RemappingIpv6IID\",(\"0\",\"1\")" in test.dut.at1.last_response)

        test.log.step("2. Set the TCP/RemappingIpv6IID setting to 1")
        test.expect(test.set_tcp_remapping(remap_mode=1))

        test.log.step("3. Check current value of TCP/RemappingIpv6IID using scfg write value "
                      "(AT^SCFG=\"TCP/RemappingIpv6IID\")")
        test.expect(test.check_tcp_remapping(expected_remap_mode=1))

        test.log.step("4. Restart module and check current value of TCP/RemappingIpv6IID using scfg write value")
        test.expect(dstl_set_full_functionality_mode(test.dut, restart=True))
        test.expect(test.check_tcp_remapping(expected_remap_mode=1))

        test.log.step("5. Set the TCP/RemappingIpv6IID setting to 0")
        test.expect(test.set_tcp_remapping(remap_mode=0))

        test.log.step("6. Check current value of TCP/RemappingIpv6IID using scfg write value "
                      "(AT^SCFG=\"TCP/RemappingIpv6IID\")")
        test.expect(test.check_tcp_remapping(expected_remap_mode=0))

        test.log.step("7. Restart module and check current value of TCP/RemappingIpv6IID using scfg write value")
        test.expect(dstl_set_full_functionality_mode(test.dut, restart=True))
        test.expect(test.check_tcp_remapping(expected_remap_mode=0))

        test.log.step("8. Optional - check if setting is described in AT Spec.")
        test.log.info("The step will be skipped in Test Script")

    def cleanup(test):
        pass

    def set_tcp_remapping(test, remap_mode):
        return test.dut.at1.send_and_verify("AT^SCFG=\"Tcp/RemappingIpv6IID\",\"{}\"".format(remap_mode))

    def check_tcp_remapping(test, expected_remap_mode):
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=\"Tcp/RemappingIpv6IID\""))
        return "\"Tcp/RemappingIpv6IID\",\"{}\"".format(expected_remap_mode) in test.dut.at1.last_response


if "__main__" == __name__:
    unicorn.main()

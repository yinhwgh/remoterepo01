#responsible: aleksander.denis@globallogic.com
#location: Wroclaw
#TC0105390.001

import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.configuration.scfg_remapping_ipv6 import dstl_enable_remapping_ipv6_iid, \
    dstl_disable_remapping_ipv6_iid, dstl_check_remapping_ipv6_iid_enabled
from dstl.configuration.set_error_message_format import dstl_set_error_message_format
from dstl.identification.get_identification import dstl_get_bootloader
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    TC intention: To check if Static IPv6 Address Allocation could be set on module and if setting
    is non-volatile.

    1. Execute the scfg=? (test) command and check output.
    2. Set the TCP/RemappingIpv6IID setting to 1
    3. Check current value of TCP/RemappingIpv6IID using scfg write value
    (AT^SCFG=”TCP/RemappingIpv6IID")
    4. Restart module and check current value of TCP/RemappingIpv6IID using scfg write value
    (AT^SCFG=”TCP/RemappingIpv6IID")
    5. Set the TCP/RemappingIpv6IID setting to 0
    6. Check current value of TCP/RemappingIpv6IID using scfg write value
    (AT^SCFG=”TCP/RemappingIpv6IID")
    7. Restart module and check current value of TCP/RemappingIpv6IID using scfg write value
    (AT^SCFG=”TCP/RemappingIpv6IID")
    8. Optional - check if setting is described in AT Spec
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_bootloader(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        dstl_set_error_message_format(test.dut)

    def run(test):
        test.log.step("1. Execute the scfg=? (test) command and check output.")
        test.expect(test.dut.at1.send_and_verify("AT^SCFG=?"))
        test.expect("\"Tcp/RemappingIpv6IID\",(\"0\",\"1\")" not in test.dut.at1.last_response)

        test.log.step("2. Set the TCP/RemappingIpv6IID setting to 1")
        test.expect(dstl_enable_remapping_ipv6_iid(test.dut))

        test.log.step("3. Check current value of TCP/RemappingIpv6IID using scfg write value "
                      "(AT^SCFG=\"TCP/RemappingIpv6IID\")")
        test.expect(dstl_check_remapping_ipv6_iid_enabled(test.dut))

        test.log.step("4. Restart module and check current value of TCP/RemappingIpv6IID using "
                      "scfg write value")
        test.expect(dstl_set_full_functionality_mode(test.dut, restart=True))
        test.expect(dstl_check_remapping_ipv6_iid_enabled(test.dut))

        test.log.step("5. Set the TCP/RemappingIpv6IID setting to 0")
        test.expect(dstl_disable_remapping_ipv6_iid(test.dut))

        test.log.step("6. Check current value of TCP/RemappingIpv6IID using scfg write value "
                      "(AT^SCFG=\"TCP/RemappingIpv6IID\")")
        test.expect(dstl_check_remapping_ipv6_iid_enabled(test.dut) == "0")

        test.log.step("7. Restart module and check current value of TCP/RemappingIpv6IID using "
                      "scfg write value")
        test.expect(dstl_set_full_functionality_mode(test.dut, restart=True))
        test.expect(dstl_check_remapping_ipv6_iid_enabled(test.dut) == "0")

        test.log.step("8. Optional - check if setting is described in AT Spec.")
        test.log.info("The step will be skipped in Test Script")

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

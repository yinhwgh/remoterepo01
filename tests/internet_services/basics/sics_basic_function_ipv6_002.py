# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0094574.002

import unicorn
from dstl.auxiliary.init import dstl_detect
from core.basetest import BaseTest
from dstl.configuration.functionality_modes import dstl_set_airplane_mode, \
    dstl_set_full_functionality_mode
from dstl.internet_service.internet_connection_setting.internet_connection_setting import \
    dstl_set_internet_connection_setting
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    Intention:
    This procedure tests the basic function of SICS under IPV6.

    Description:
    1. Execute test command: AT^SICS=? , check OK response.
    2. Execute read command AT^SICS? , check if response is correct.
    3. Execute write command AT^SICS=x, ipv6dns1,[] use dynamic DNS assignment.
    - Check valid value of x is 1~16.
    4. Set ipv6dns1 with [] and set ipv6dns2 manually, for example:
    - AT^SICS=x,ipv6dns1,[]
    - AT^SICS=x,ipv6dns2,ipv6 address
    5. Set ipv6dns2 with [] and set ipv6dns1 manually, for example:
    - AT^SICS=x,ipv6dns1,ipv6 address
    - AT^SICS=x,ipv6dns2,[]
    6. Set ipv6dns2 and ipv6dns1 manually, for example:
    - AT^SICS=x, ipv6dns1,ipv6 address
    - AT^SICS=x, ipv6dns2,ipv6 address
    7. Set cid with invalid value like: 0, 17, -1 and etc. Error will return.
    8. Switch to airplane mode, check if AT^SICS command can be executed.
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_enter_pin(test.dut)
        test.sics_range = 17
        test.error = "+CME ERROR:"
        test.read_response = \
            '^SICS: 1,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 1,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 2,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 2,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 3,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 3,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 4,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 4,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 5,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 5,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 6,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 6,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 7,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 7,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 8,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 8,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 9,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 9,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 10,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 10,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 11,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 11,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 12,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 12,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 13,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 13,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 14,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 14,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 15,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 15,"ipv6dns2","[2001:abab::1]"\r\n' \
            '^SICS: 16,"ipv6dns1","[2001:abab::1]"\r\n^SICS: 16,"ipv6dns2","[2001:abab::1]"'
        test.dns_addresses = ['', '2001:abab::1', '2001:abab:cdcd:efe0:1234:5678:9012:ab12']

    def run(test):
        test.log.info("TC0094574.002 SICSBasicFunction_IPV6")
        test.log.step('1. Execute test command: AT^SICS=? , check OK response.')
        test.expect(test.dut.at1.send_and_verify('AT^SICS=?', expect="OK"))

        test.log.step('2. Execute read command AT^SICS? , check if response is correct.')
        test.expect(test.dut.at1.send_and_verify('AT^SICS?', expect="OK"))

        test.log.step('3. Execute write command AT^SICS=x, ipv6dns1,[], use dynamic DNS '
                      'assignment.\r\n- Check valid value of x is 1~16.')
        for i in range(1, test.sics_range):
            test.expect(dstl_set_internet_connection_setting(test.dut, i, "ipv6dns1",
                                                             test.dns_addresses[0]))

        test.log.step('4. Set ipv6dns1 with [] and set ipv6dns2 manually, for example:\r\n'
                      '- AT^SICS=x,ipv6dns1,[]\r\n- AT^SICS=x,ipv6dns2,ipv6 address')
        test.set_dns_v6(test.dns_addresses[0],test.dns_addresses[2])

        test.log.step('5. Set ipv6dns2 with [] and set ipv6dns1 manually, for example:\r\n'
                      '- AT^SICS=x,ipv6dns1,ipv6 address\r\n- AT^SICS=x,ipv6dns2,[]')
        test.set_dns_v6(test.dns_addresses[2], test.dns_addresses[0])

        test.log.step('6. Set ipv6dns2 and ipv6dns1 manually, for example:\r\n'
                      '- AT^SICS=x, ipv6dns1,ipv6 address\r\n- AT^SICS=x, ipv6dns2,ipv6 address')
        test.set_dns_v6(test.dns_addresses[1], test.dns_addresses[1])

        test.log.step('7. Set cid with invalid value like: 0, 17, -1 and etc. Error will return.')
        test.expect(test.dut.at1.send_and_verify('AT^SICS=0,"ipv6dns1","2001:abab::1"',
                                                 expect=test.error))
        test.expect(test.dut.at1.send_and_verify('AT^SICS=17,"ipv6dns2","2001:abab::1"',
                                                 expect=test.error))
        test.expect(test.dut.at1.send_and_verify('AT^SICS=-1,"ipv6dns1","2001:abab::1"',
                                                 expect=test.error))

        test.log.step('8. Switch to airplane mode, check if AT^SICS command can be executed.')
        test.expect(dstl_set_airplane_mode(test.dut))
        test.expect(test.dut.at1.send_and_verify('AT^SICS=?', expect="OK"))
        test.expect(test.dut.at1.send_and_verify('AT^SICS?', expect=test.read_response))
        test.set_dns_v6(test.dns_addresses[0], test.dns_addresses[0])

    def cleanup(test):
        dstl_set_full_functionality_mode(test.dut)
        test.set_dns_v6(test.dns_addresses[0], test.dns_addresses[0])

    def set_dns_v6(test,dns_1,dns_2):
        for i in range(1, test.sics_range):
            test.expect(dstl_set_internet_connection_setting(test.dut, i, "ipv6dns1", dns_1))
            test.expect(dstl_set_internet_connection_setting(test.dut, i, "ipv6dns2", dns_2))


if "__main__" == __name__:
    unicorn.main()
#responsible sebastian.lupkowski@globallogic.com
#Wroclaw
#TC 0011199.001
import unicorn

from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.network_service.register_to_network import dstl_enter_pin
from dstl.identification.get_imei import dstl_get_imei
from dstl.auxiliary.restart_module import dstl_restart


class Test(BaseTest):
    """
    TC0011199.001    SelectPreferredMemoryStorage

    To test the +CPMS command for supported values.

    1. Set AT+CPMS="ME","ME","ME"
    2. Check AT+CPMS?
    3. Restart module
    4. Check AT+CPMS?
    5. Repeat steps 1-4 for all combinations of supported <mem1>,<mem2>,<mem3> values
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)
        dstl_set_full_functionality_mode(test.dut)
        test.expect(dstl_enter_pin(test.dut))
        test.sleep(15)  # waiting for module to get ready
        test.expect(test.dut.at1.send_and_verify("AT+CMEE=2", ".*OK.*"))

    def run(test):
        memory = ["ME", "MT", "SM", "SR"]
        for slot1 in memory:
            for slot2 in memory:
                for slot3 in memory:
                    test.log.step('1. Set AT+CPMS="{0}","{1}","{2}"'.format(slot1, slot2, slot3))
                    check_cpms(test, 'write', '"{0}","{1}","{2}"'.format(slot1, slot2, slot3))
                    test.log.step('2. Check AT+CPMS?')
                    check_cpms(test, 'read', '"{0}",.*"{1}",.*"{2}"'.format(slot1, slot2, slot3))
                    test.log.step('3. Restart module')
                    test.expect(dstl_restart(test.dut))
                    test.expect(dstl_enter_pin(test.dut))
                    test.sleep(15)  # waiting for module to get ready
                    test.log.step('4. Check AT+CPMS?')
                    check_cpms(test, 'read', '"{0}",.*"{1}",.*"{2}"'.format(slot1, slot2, slot3))
                    if not (slot1 == slot2 == slot3 == memory[-1]):
                        test.log.step('5. Repeat steps 1-4 for all combinations of supported <mem1>,<mem2>,<mem3> '
                                      'values')

    def cleanup(test):
        check_cpms(test, 'write', '"ME","ME","ME"')
        test.expect(test.dut.at1.send_and_verify("AT&F", ".*OK.*"))
        test.expect(test.dut.at1.send_and_verify("AT&W", ".*OK.*"))


def check_cpms(test, mode, value):
    if mode is 'write':
        test.expect(test.dut.at1.send_and_verify("AT+CPMS={}".format(value), ".*OK.*"))
    else:
        test.expect(test.dut.at1.send_and_verify("AT+CPMS?", ".*\\+CPMS: {}.*OK.*".format(value)))


if "__main__" == __name__:
    unicorn.main()

# responsible: michal.habrych@globallogic.com
# location: Wroclaw
# TC0107932.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification.get_identification import dstl_get_defined_manufacturer
from dstl.identification.get_imei import dstl_get_imei


class Test(BaseTest):
    """
    Intention:
    To check if SCFG Id/Manufacturer parameter display correct name

    Description:
    1) Check product identification information using ATI command
    2) Check Id/Manufacturer using at^scfg="Id/Manufacturer" and compare with ATI answer
    """

    def setup(test):
        dstl_detect(test.dut)
        dstl_get_imei(test.dut)

    def run(test):
        test.log.info('TC0107932.001 IdManufacturer_basic')
        expected_name = dstl_get_defined_manufacturer(test.dut)
        test.log.step('1) Check product identification information using ATI command')
        test.expect(test.dut.at1.send_and_verify("ATI", expect=expected_name, wait_for="OK"))

        test.log.step('2) Check Id/Manufacturer using at^scfg="Id/Manufacturer" and compare with '
                      'ATI answer')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG=\"Id/Manufacturer\"',
                                            expect=expected_name, wait_for="OK"))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

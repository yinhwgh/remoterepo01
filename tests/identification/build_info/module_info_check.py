# responsible: xiaoyu.chen@thalesgroup.com
# location: Dalian
# TC0088284.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary import init
from dstl.identification import get_identification
from dstl.identification import get_imei


class Test(BaseTest):
    """
     TC0088284.001 - TpModuleInfo
     Intention: Read out all module relevant information.
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        # SW version, bootloader, ati...
        test.dut.at1.send_and_verify('at^sos=ver', '.*OK.*')
        test.expect(test.dut.at1.send_and_verify('at^cicret=SWN', '.*O.*'))
        test.expect(test.dut.at1.send_and_verify('ati', '.*Cinterion.*REVISION.*OK.*'))
        test.dut.at1.send_and_verify('at^sos=bootloader/info', test.dut.dstl_get_defined_bootloader())

        test.log.info('Test all supported ati parameter, should define in devconfig file')
        for i in test.dut.dstl_get_defined_ati_parameters():
            if i in [1, 51, 176, 281]:
                if i == 1:
                    test.expect(test.dut.at1.send_and_verify('ati1', '.*Cinterion.*REVISION.*A-REVISION.*OK.*'))
                if i == 51:
                    test.expect(test.dut.at1.send_and_verify('ati51', test.dut.dstl_get_defined_bootloader()))
                if i == 176:
                    test.expect(test.dut.at1.send_and_verify('ati176', test.dut.dstl_get_imei() + '\.\d{2}'))
                if i == 281:
                    test.expect(test.dut.at1.send_and_verify('ati281', test.dut.dstl_get_defined_sachnummer()))
            else:
                test.dut.at1.send_and_verify('ati{}'.format(i), 'OK')

        test.expect(test.dut.at1.send_and_verify('at&f', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at&w', '.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgmm', f'{test.dut.product}-{test.dut.variant}'))
        test.expect(test.dut.at1.send_and_verify('at+cgmr', '.*REVISION.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgmi', '.*Cinterion.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at+cgsn', '.*\d{15}.*OK.*'))
        test.expect(test.dut.at1.send_and_verify('at^ssvn', '.*O.*'))

        # SDPORT? need adapt for a certain product
        test.expect(test.dut.at1.send_and_verify('at^sdport?', 'OK|ERROR'))

        # HWID? need adapt for a certain product
        test.expect(test.dut.at1.send_and_verify('at^sos=adc/hwid', 'OK|ERROR'))

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()

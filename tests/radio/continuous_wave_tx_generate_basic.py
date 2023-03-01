#responsible: mariusz.wojcik@globallogic.com
#location: Wroclaw
#TC0094871.001

import unicorn
from core.basetest import BaseTest
from dstl.auxiliary.init import dstl_detect
from dstl.identification import get_imei
from dstl.configuration.functionality_modes import dstl_set_full_functionality_mode
from dstl.auxiliary import restart_module


class Test(BaseTest):
    """
    Check if the module is able to generating continuous wave (CW) signal.

    1. Set AT+CFUN=5 to switch to the Factory Test Mode.
    2. Run the generating CW on the module, using command: AT^SCFG= "MEopMode/CT"[,<cwMode>[,<cwReserved>,<cwLevel>,<cwUarfcn>] ]
    and check if the signal is generated and module returns "OK".
    3. Stop generating of signal by command: AT^SCFG="MEopMode/CT",0.
    4. Leave the Factory Test Mode using using AT+CFUN=1.
    """

    def setup(test):
        test.dut.dstl_detect()
        test.dut.dstl_get_imei()

    def run(test):
        test.log.step('1. Set AT+CFUN=5 to switch to the Factory Test Mode.')
        test.expect(test.dut.at1.send_and_verify('AT+CFUN=5', '.*OK.*', wait_for="SYSSTART FACTORY TEST MODE"))

        test.log.step('2. Run the generating CW on the module, using command: '
                      'AT^SCFG= "MEopMode/CT"[,<cwMode>[,<cwReserved>,<cwLevel>,<cwUarfcn>]] '
                      'and check if the signal is generated and module returns "OK"')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CT","1","","18","27125"', '.*OK.*'))

    def cleanup(test):
        test.log.step('3. Stop generating of signal by command: AT^SCFG="MEopMode/CT","0".')
        test.expect(test.dut.at1.send_and_verify('AT^SCFG="MEopMode/CT","0"', '.*OK.*'))

        test.log.step('4. Leave the Factory Test Mode using using AT+CFUN=1.')
        test.expect(test.dut.dstl_set_full_functionality_mode())
        test.expect(test.dut.dstl_restart())


if "__main__" == __name__:
    unicorn.main()

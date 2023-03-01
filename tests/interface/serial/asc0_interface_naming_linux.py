#responsible: agata.mastalska@globallogic.com
#location: Wroclaw
#TC0104598.001

import unicorn
from core.basetest import BaseTest
from dstl.configuration import shutdown_smso
from dstl.auxiliary import restart_module
from dstl.auxiliary.devboard import devboard


def check_module_correct_presented(test):
    test.log.info("Checking if module is presented as ttyS0")
    test.expect("ttyS0" in test.os.execute('ls /dev/'))


class Test(BaseTest):
    """
    TC0104598.001 Asc0InterfaceNaming_Linux
    Checking name of Asc0 interface on Linux 0S
    responsible: agata.mastalska@globallogic.com
    location: Wroclaw
    """

    def setup(test):
        test.dut.dstl_detect()

    def run(test):
        test.log.step('1. Switch on and connect module via ASC0 to PC.')
        test.expect(test.dut.at1.send_and_verify("AT", "OK", timeout=30))
        test.log.step('2. Open Terminal Adapter and check that module is presented as ttyS0.')
        check_module_correct_presented(test)
        test.log.step('3. Restart module by AT+CFUN=1,1')
        test.expect(test.dut.dstl_restart())
        test.log.step('4. Repeat step 2.')
        check_module_correct_presented(test)
        test.log.step('5. Turn off module via AT^SMSO')
        test.dut.dstl_shutdown_smso()
        test.log.step('6. Turn ON module via IGT')
        test.expect(test.dut.dstl_turn_on_igt_via_dev_board())
        test.log.step('7. Repeat step 2.')
        check_module_correct_presented(test)

    def cleanup(test):
        pass


if "__main__" == __name__:
    unicorn.main()
